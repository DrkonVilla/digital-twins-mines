"""
Perfilador de hardware y benchmark de latencia multiagente (FON-10).

Registra de forma auditable el entorno exacto (CPU, núcleos, RAM, GPU/VRAM, SO, Python y
versiones de librerías) y mide la latencia de un ciclo de inferencia a 5 Hz con
N agentes simultáneos (por defecto 50/100/200/500):

  - inferencia: predict_proba del XGBoost entrenado con el protocolo oficial
  - serialización: json.dumps de las N alertas
  - transporte: ida y vuelta por WebSocket en loopback (si `websockets` está disponible)

Se reportan P50/P95/P99/máx y el % de ciclos dentro del presupuesto de 200 ms.

LIMITACIÓN (se declara en el JSON): los FPS de renderizado Three.js/InstancedMesh sólo se
pueden medir en el navegador; este script NO los inventa. Deja `frontend_fps = null`
hasta incorporar la medición del lado cliente. El transporte es loopback local, no una
red de mina real.

Salida (versionada en git): results/hardware_specs_benchmark.json
"""
import argparse
import asyncio
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib import metadata

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fair_eval as fe  # noqa: E402

BUDGET_MS = 200.0
TICK_HZ = 5.0


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=25, shell=isinstance(cmd, str)).stdout.strip()
    except Exception:
        return ""


def _pkg(name):
    try:
        return metadata.version(name)
    except Exception:
        return None


def collect_system_info():
    import psutil
    info = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "os": platform.platform(), "os_version": platform.version(), "machine": platform.machine(),
        "python": sys.version.split()[0], "python_implementation": platform.python_implementation(),
        "cpu_logical_cores": psutil.cpu_count(logical=True),
        "cpu_physical_cores": psutil.cpu_count(logical=False),
        "ram_total_gb": round(psutil.virtual_memory().total / 1024 ** 3, 2),
        "ram_available_gb": round(psutil.virtual_memory().available / 1024 ** 3, 2),
    }
    freq = psutil.cpu_freq()
    if freq:
        info["cpu_freq_mhz_current"] = round(freq.current, 0)
        info["cpu_freq_mhz_max"] = round(freq.max, 0) if freq.max else None

    if sys.platform.startswith("win"):
        ps = lambda q: _run(["powershell", "-NoProfile", "-Command", q])
        info["cpu_model"] = ps("(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)") or platform.processor()
        gpus = ps("Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + '|' + $_.AdapterRAM + '|' + $_.DriverVersion } ")
        info["gpus"] = [dict(zip(("name", "adapter_ram_bytes_wmi_may_cap_at_4GB", "driver_version"), line.split("|")))
                        for line in gpus.splitlines() if line.strip()]
    else:
        lscpu = _run("lscpu")
        info["cpu_model"] = next((l.split(":", 1)[1].strip() for l in lscpu.splitlines() if "Model name" in l), platform.processor())
        info["gpus"] = [{"name": l.strip()} for l in _run("lspci | grep -i -E 'vga|3d'").splitlines()]

    if shutil.which("nvidia-smi"):
        smi = _run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
        info["nvidia_smi"] = [dict(zip(("name", "vram_total", "driver_version"), [x.strip() for x in l.split(",")]))
                              for l in smi.splitlines() if l.strip()]
    else:
        info["nvidia_smi"] = None

    info["libraries"] = {p: _pkg(p) for p in (
        "numpy", "pandas", "scikit-learn", "xgboost", "imbalanced-learn", "scipy", "shap", "psutil",
        "websockets", "fastapi", "uvicorn", "langchain", "langchain-google-genai", "google-generativeai")}
    return info


def _summ(a):
    a = np.asarray(a)
    return {"mean": float(a.mean()), "p50": float(np.percentile(a, 50)), "p95": float(np.percentile(a, 95)),
            "p99": float(np.percentile(a, 99)), "max": float(a.max()),
            "pct_within_budget": float((a <= BUDGET_MS).mean() * 100)}


async def _ws_roundtrip_ms(payloads, n_warm=3):
    """Tiempos (ms) de ida y vuelta por WebSocket en loopback para cada payload."""
    try:
        import websockets
    except Exception as e:
        return None, f"websockets no disponible: {e}"
    try:
        try:
            from websockets.asyncio.server import serve
            from websockets.asyncio.client import connect

            async def handler(ws):
                async for msg in ws:
                    await ws.send(msg)
        except Exception:
            from websockets import serve, connect  # API heredada

            async def handler(ws, *a):
                async for msg in ws:
                    await ws.send(msg)

        times = []
        async with serve(handler, "127.0.0.1", 0, max_size=None) as server:
            port = list(server.sockets)[0].getsockname()[1] if hasattr(server, "sockets") else server.server.sockets[0].getsockname()[1]
            async with connect(f"ws://127.0.0.1:{port}", max_size=None) as ws:
                for i, p in enumerate(payloads):
                    t0 = time.perf_counter()
                    await ws.send(p)
                    await ws.recv()
                    dt = (time.perf_counter() - t0) * 1000.0
                    if i >= n_warm:
                        times.append(dt)
        return times, None
    except Exception as e:
        return None, f"fallo del benchmark WebSocket: {type(e).__name__}: {e}"


def benchmark(agent_counts, ticks, seed=fe.RANDOM_STATE):
    df = fe.load_dataset()
    X_train, X_test, y_train, _ = fe.split_train_test(df)
    print("Entrenando XGBoost (protocolo oficial) para el benchmark...", flush=True)
    pipe = fe.make_pipeline("XGBoost")
    pipe.fit(np.asarray(X_train, float), np.asarray(y_train))
    pool = np.asarray(X_test, float)
    rng = np.random.default_rng(seed)

    results = {}
    for n in agent_counts:
        X = pool[rng.integers(0, len(pool), size=(ticks + 5, n))]
        infer, ser, total_cpu, payloads = [], [], [], []
        for t in range(ticks + 5):
            t0 = time.perf_counter()
            proba = pipe.predict_proba(X[t])
            t1 = time.perf_counter()
            msg = json.dumps([{"agent": i, "risk": int(np.argmax(p)), "p_alto": round(float(p[2]), 4)}
                              for i, p in enumerate(proba)])
            t2 = time.perf_counter()
            if t >= 5:  # descarta calentamiento
                infer.append((t1 - t0) * 1000.0)
                ser.append((t2 - t1) * 1000.0)
                payloads.append(msg)
        ws_times, ws_err = asyncio.run(_ws_roundtrip_ms(payloads, n_warm=0))
        cpu_total = np.array(infer) + np.array(ser)
        e2e = cpu_total + (np.array(ws_times) if ws_times else 0.0)
        results[str(n)] = {
            "agents": n, "ticks_measured": len(infer), "tick_rate_hz": TICK_HZ, "budget_ms": BUDGET_MS,
            "inference_ms": _summ(infer), "serialization_ms": _summ(ser),
            "websocket_loopback_roundtrip_ms": _summ(ws_times) if ws_times else None,
            "websocket_error": ws_err,
            "end_to_end_ms": _summ(e2e),
            "payload_bytes": int(np.mean([len(p) for p in payloads])),
        }
        e = results[str(n)]["end_to_end_ms"]
        print(f"N={n:<4} E2E P50={e['p50']:.1f} P95={e['p95']:.1f} P99={e['p99']:.1f} ms | "
              f"dentro de {BUDGET_MS:.0f} ms: {e['pct_within_budget']:.1f} %", flush=True)
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agents", type=int, nargs="*", default=[50, 100, 200, 500])
    ap.add_argument("--ticks", type=int, default=300)
    a = ap.parse_args()

    print("=" * 72 + "\nPERFIL DE HARDWARE Y BENCHMARK DE LATENCIA\n" + "=" * 72)
    system = collect_system_info()
    print(json.dumps({k: system[k] for k in ("os", "cpu_model", "cpu_physical_cores", "cpu_logical_cores",
                                              "ram_total_gb", "python")}, indent=2, ensure_ascii=False))
    out = {
        "system": system,
        "benchmark": benchmark(a.agents, a.ticks),
        "frontend_fps": None,
        "limitations": [
            "FPS de Three.js/InstancedMesh NO medido aquí (requiere el navegador); no se reportan cifras inventadas.",
            "El transporte es WebSocket en loopback local; no refleja una red subterránea real.",
            "Los agentes son muestras del conjunto de prueba, no telemetría operativa real.",
            "Se mide una sola máquina; repetir en el hardware objetivo antes de generalizar.",
        ],
    }
    fe.dump_json(out, fe.RESULTS_DIR / "hardware_specs_benchmark.json")
    print("\nGuardado: results/hardware_specs_benchmark.json")


if __name__ == "__main__":
    main()
