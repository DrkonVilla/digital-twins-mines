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
                "direction_worker": 2, "direction_machine": 6,
                "distance_3d": 35.0, "ttc": 45.0,
                "worker_speed": 0.8, "machine_speed": 2.0, "relative_speed": 2.8,
                "in_restricted_zone": 0, "machine_status": 1,
                "worker_bpm": 76.0, "hrv_ms": 65.0, "eye_blink_rate": 14.0, "fixation_duration_ms": 380.0, "fatigue_index": 0.15,
                "vibration_rms": 0.8, "acceleration_z": 9.81, "machine_slope_angle": 1.2, "wall_distance": 2.5,
                "gas_co_ppm": 8.0, "gas_no2_ppm": 0.4, "dust_density_mg_m3": 0.8, "ambient_light_lux": 85.0, "ntp_sync_precision_ms": 1.0
            }
        },
        # Escenario 2: Advertencia (Fatiga + Proximidad Moderada + Inclinación)
        {
            "name": "🟡 Advertencia por Proximidad, Fatiga y Reducción de Atención Ocular",
            "data": {
                "worker_id": 1, "machine_id": 1,
                "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
                "machine_x": 12.0, "machine_y": 0.0, "machine_z": 0.0,
                "direction_worker": 1, "direction_machine": 5,
                "distance_3d": 12.0, "ttc": 12.0,
                "worker_speed": 1.2, "machine_speed": 4.0, "relative_speed": 5.2,
                "in_restricted_zone": 1, "machine_status": 1,
                "worker_bpm": 115.0, "hrv_ms": 32.0, "eye_blink_rate": 28.0, "fixation_duration_ms": 190.0, "fatigue_index": 0.48,
                "vibration_rms": 1.8, "acceleration_z": 9.81, "machine_slope_angle": 5.5, "wall_distance": 1.2,
                "gas_co_ppm": 22.0, "gas_no2_ppm": 1.8, "dust_density_mg_m3": 2.1, "ambient_light_lux": 40.0, "ntp_sync_precision_ms": 1.0
            }
        },
        # Escenario 3: Riesgo Crítico (Colisión Inminente + Particle Filter CRITICO_30S + Protocolo What-If)
        {
            "name": "🔴 ALERTA CRÍTICA: Peligro de Atropello + Fatiga Alta + Pendiente + Visibilidad Baja (Colisión +30s)",
            "data": {
                "worker_id": 1, "machine_id": 1,
                "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
                "machine_x": 4.0, "machine_y": 0.0, "machine_z": 0.0,
                "direction_worker": 0,
                "direction_machine": 4,
                "distance_3d": 4.0, "ttc": 0.8,
                "worker_speed": 0.5, "machine_speed": 4.5, "relative_speed": 5.0,
                "in_restricted_zone": 1, "machine_status": 1,
                "worker_bpm": 145.0, "hrv_ms": 14.0, "eye_blink_rate": 42.0, "fixation_duration_ms": 95.0, "fatigue_index": 0.88,
                "vibration_rms": 3.2, "acceleration_z": 9.81, "machine_slope_angle": 10.2, "wall_distance": 0.8,
                "gas_co_ppm": 65.0, "gas_no2_ppm": 4.5, "dust_density_mg_m3": 5.5, "ambient_light_lux": 10.0, "ntp_sync_precision_ms": 1.0
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
