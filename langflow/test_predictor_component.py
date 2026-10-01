import os
import sys

# Agregar paths para importar
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from components.mining_risk_predictor import MiningRiskPredictorComponent

def main():
    print("=" * 60)
    print("Probando Componente de Langflow para Modelos Predictivos M-11")
    print("=" * 60)

    # Instanciamos el componente con parámetros de riesgo alto
    component = MiningRiskPredictorComponent()
    component.distance_3d = 2.8
    component.ttc = 1.4
    component.machine_speed = 4.2
    component.worker_speed = 1.0
    component.in_restricted_zone = 1
    component.gas_co_ppm = 42.0
    component.fatigue_index = 0.75
    component.worker_bpm = 120.0
    component.dust_density_mg_m3 = 5.0

    print("\n1. Ejecutando inferencia sobre el modelo .joblib...")
    data_output = component.predict_risk()
    print("   Resultado estructurado:")
    for k, v in data_output.data.items():
        if k != "inputs":
            print(f"   - {k}: {v}")

    print("\n2. Generando mensaje diagnóstico para el LLM / Langflow:")
    msg = component.generate_diagnostic_text()
    print("-" * 50)
    print(msg.text)
    print("-" * 50)
    print("\n✅ ¡Componente de Langflow verificado con éxito!")

if __name__ == "__main__":
    main()
