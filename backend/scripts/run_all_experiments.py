"""
Master Experiment Runner for M-11 Scientific Replication.

Executes all experimental modules in sequential order and regenerates
all scientific deliverables in results/ and figures/.
"""
import sys
import subprocess
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parent

EXPERIMENT_SCRIPTS = [
    ("1. Symmetric Model Evaluation & Baselines", "train_cv.py"),
    ("2. Multimodal Ablation Study (Configs A to G)", "run_ablation_study.py"),
    ("3. Label Circularity Audit & Decoupled Scenarios", "audit_label_circularity.py"),
    ("4. TreeSHAP & Feature Collinearity Analysis", "run_shap_and_collinearity.py"),
    ("5. Hardware & Latency Benchmark Profiler", "benchmark_hardware_profiler.py"),
    ("6. GenAI Gemini Emergency Protocol Audit", "audit_genai_protocol.py"),
    ("7. Master Deliverables & Figures Compiler", "generate_all_deliverables.py"),
]


def run_step(step_name, script_filename):
    script_path = SCRIPTS_DIR / script_filename
    print(f"\n=======================================================")
    print(f"--> [RUNNING] {step_name} ({script_filename})")
    print(f"=======================================================")
    
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    elapsed = time.time() - t0
    
    if result.stdout:
        print(result.stdout.strip())
        
    if result.returncode != 0:
        print(f"\n[ERROR] Step {script_filename} failed with returncode {result.returncode}!")
        if result.stderr:
            print(f"[STDERR]:\n{result.stderr.strip()}")
        sys.exit(result.returncode)
    else:
        print(f"--> [COMPLETED] in {elapsed:.2f} seconds.")


def main():
    print("*****************************************************************")
    print(" M-11 SCIENTIFIC EXPERIMENTAL REPLICATION PIPELINE")
    print(" Target Journal: Acta Montanistica Slovaca")
    print(" Python Version:", sys.version.split()[0])
    print(" Workspace:", PROJECT_ROOT)
    print("*****************************************************************")
    
    start_total = time.time()
    for name, script in EXPERIMENT_SCRIPTS:
        run_step(name, script)
        
    total_elapsed = time.time() - start_total
    print("\n*****************************************************************")
    print(f" ALL M-11 EXPERIMENTAL ARTIFACTS SUCCESSFULLY REGENERATED!")
    print(f" Total pipeline runtime: {total_elapsed / 60:.2f} minutes.")
    print(" Check results in: results/")
    print(" Check figures in: figures/")
    print(" Check reports in: reports/")
    print("*****************************************************************")


if __name__ == "__main__":
    main()
