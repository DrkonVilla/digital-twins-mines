import requests
import time
import random
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

def run_simulation():
    print("================================================================================")
    print("SIMULADOR EN VIVO DE TELEMETRÍA Y RIESGO PARA EL GEMELO DIGITAL 3D (M-11)")
    print("================================================================================")

    # 1. Obtener Token JWT de autenticación
    print("\n[1/2] Autenticando en el sistema M-11...")
    auth_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
        if res.status_code != 200:
            print(f"❌ Error al iniciar sesión: {res.text}")
            return
        
        token = res.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        print("✅ Autenticación exitosa. Token Bearer obtenido.")

    except Exception as e:
        print(f"❌ Error conectando al servidor Backend: {e}")
        return

    # 2. Enviar secuencia de telemetría simulada
    print("\n[2/2] Enviando telemetría simulada en tiempo real hacia el Gemelo 3D...")
    print("Mira la pestaña http://localhost:3000/gemelo-digital mientras se ejecutan los envíos:\n")

    scenarios = [
        # Escenario 1: Normal
        {
            "name": "🟢 Operación Normal (Bajo Riesgo)",
            "data": {
                "worker_id": 1, "machine_id": 1,
                "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
                "machine_x": 35.0, "machine_y": 0.0, "machine_z": 0.0,
                "direction_worker": 2, "direction_machine": 6,  # Trayectoria de alejamiento seguro (Norte vs Sur)
                "distance_3d": 35.0, "ttc": 45.0,
                "worker_speed": 0.8, "machine_speed": 2.0, "relative_speed": 2.8,
                "in_restricted_zone": 0, "machine_status": 1,
                "worker_bpm": 76.0, "fatigue_index": 0.15,
                "gas_co_ppm": 8.0, "dust_density_mg_m3": 0.8
            }
        },
        # Escenario 2: Advertencia (Fatiga + Proximidad Moderada)
        {
            "name": "🟡 Advertencia por Proximidad e Incremento de BPM",
            "data": {
                "worker_id": 1, "machine_id": 1,
                "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
                "machine_x": 12.0, "machine_y": 0.0, "machine_z": 0.0,
                "direction_worker": 1, "direction_machine": 5,
                "distance_3d": 12.0, "ttc": 12.0,
                "worker_speed": 1.2, "machine_speed": 4.0, "relative_speed": 5.2,
                "in_restricted_zone": 1, "machine_status": 1,
                "worker_bpm": 115.0, "fatigue_index": 0.48,
                "gas_co_ppm": 22.0, "dust_density_mg_m3": 2.1
            }
        },
        # Escenario 3: Riesgo Crítico (Colisión Inminente + Particle Filter CRITICO_30S)
        {
            "name": "🔴 ALERTA CRÍTICA: Peligro de Atropello + Fatiga Alta + Gas CO (Colisión +30s)",
            "data": {
                "worker_id": 1, "machine_id": 1,
                "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
                "machine_x": 4.0, "machine_y": 0.0, "machine_z": 0.0,
                "direction_worker": 0,   # El trabajador avanza en +X hacia la máquina
                "direction_machine": 4,  # La máquina avanza en -X hacia el trabajador
                "distance_3d": 4.0, "ttc": 0.8,
                "worker_speed": 0.5, "machine_speed": 4.5, "relative_speed": 5.0,
                "in_restricted_zone": 1, "machine_status": 1,
                "worker_bpm": 145.0, "fatigue_index": 0.88,
                "vibration_rms": 3.2, "acceleration_z": 9.81,
                "gas_co_ppm": 65.0, "dust_density_mg_m3": 5.5, "ambient_light_lux": 15.0
            }
        }
    ]

    for step, item in enumerate(scenarios, 1):
        print(f"--- Pasó {step}: {item['name']} ---")
        res = requests.post(f"{BASE_URL}/predict/", json=item["data"], headers=headers)
        if res.status_code == 200:
            out = res.json()
            print(f"   [API 200 OK] Riesgo Clasificado: {out['risk_level']} ({out['risk_score']}%)")
        else:
            print(f"   [Error {res.status_code}] {res.text}")
        
        time.sleep(3)

    print("\n================================================================================")
    print("Simulación finalizada. Revisa la pantalla 3D en http://localhost:3000/gemelo-digital")
    print("================================================================================")

if __name__ == "__main__":
    run_simulation()
