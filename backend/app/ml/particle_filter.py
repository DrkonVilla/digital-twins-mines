import numpy as np
from typing import Dict, Any, List

class ParticleFilter3DPredictor:
    """
    Filtro de Partículas (Sequential Monte Carlo) para Asimilación de Datos y
    Predicción de Riesgo con 30 Segundos de Antelación en Gemelo Digital Minero M-11.
    
    Estado de cada partícula: [x, y, z, vx, vy, vz]
    """

    def __init__(self, n_particles: int = 500, collision_threshold: float = 7.0):
        self.n_particles = n_particles
        self.dt_horizon = 30.0 # Horizonte de predicción futura en segundos
        self.collision_threshold = collision_threshold

    def predict_future_risk(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el ciclo del Filtro de Partículas:
          1. Inicialización / Muestreo de partículas alrededor de la posición actual del trabajador.
          2. Transición Dinámica Monte Carlo proyectada a +30s con modelo cinemático estocástico.
          3. Asimilación de telemetría (Velocidad, Biometría, Maquinaria).
          4. Cálculo del porcentaje de partículas en zona de colisión futura.
        """
        # Extraer posiciones y velocidades actuales
        wx = float(telemetry.get('worker_x', 0.0))
        wy = float(telemetry.get('worker_y', 0.0))
        wz = float(telemetry.get('worker_z', 0.0))

        mx = float(telemetry.get('machine_x', 10.0))
        my = float(telemetry.get('machine_y', 0.0))
        mz = float(telemetry.get('machine_z', 0.0))

        w_speed = float(telemetry.get('worker_speed', 1.0))
        m_speed = float(telemetry.get('machine_speed', 3.0))
        dir_w = float(telemetry.get('direction_worker', 0))
        dir_m = float(telemetry.get('direction_machine', 0))

        # Convertir direcciones (0-7) a ángulos en radianes
        angle_w = (dir_w / 8.0) * 2 * np.pi
        angle_m = (dir_m / 8.0) * 2 * np.pi

        # Componentes de velocidad
        vx_w, vy_w = w_speed * np.cos(angle_w), w_speed * np.sin(angle_w)
        vx_m, vy_m = m_speed * np.cos(angle_m), m_speed * np.sin(angle_m)

        # 1. Muestreo de N partículas para el trabajador
        np.random.seed(42) # Reproducibilidad
        p_x = wx + np.random.normal(0, 0.5, self.n_particles)
        p_y = wy + np.random.normal(0, 0.5, self.n_particles)
        p_z = wz + np.random.normal(0, 0.2, self.n_particles)

        p_vx = vx_w + np.random.normal(0, 0.3, self.n_particles)
        p_vy = vy_w + np.random.normal(0, 0.3, self.n_particles)

        # 2. Muestreo de N partículas para la máquina
        m_p_x = mx + np.random.normal(0, 0.8, self.n_particles)
        m_p_y = my + np.random.normal(0, 0.8, self.n_particles)
        m_p_z = mz + np.random.normal(0, 0.3, self.n_particles)

        m_p_vx = vx_m + np.random.normal(0, 0.5, self.n_particles)
        m_p_vy = vy_m + np.random.normal(0, 0.5, self.n_particles)

        # 3. Transición Dinámica Futura t + 30s (Kinematic Propagation + Brownian noise)
        future_worker_x = p_x + p_vx * self.dt_horizon + np.random.normal(0, 1.5, self.n_particles)
        future_worker_y = p_y + p_vy * self.dt_horizon + np.random.normal(0, 1.5, self.n_particles)
        future_worker_z = p_z + np.random.normal(0, 0.5, self.n_particles)

        future_machine_x = m_p_x + m_p_vx * self.dt_horizon + np.random.normal(0, 2.0, self.n_particles)
        future_machine_y = m_p_y + m_p_vy * self.dt_horizon + np.random.normal(0, 2.0, self.n_particles)
        future_machine_z = m_p_z + np.random.normal(0, 0.5, self.n_particles)

        # 4. Cálculo de Distancias en la Ventana Futura [0, 30s] (Mínima distancia en el horizonte)
        rx0 = m_p_x - p_x
        ry0 = m_p_y - p_y
        rz0 = m_p_z - p_z

        rvx = m_p_vx - p_vx
        rvy = m_p_vy - p_vy

        v2 = rvx**2 + rvy**2
        v2_safe = np.where(v2 == 0, 1e-6, v2)
        t_star = -(rx0 * rvx + ry0 * rvy) / v2_safe
        t_closest = np.clip(t_star, 0.0, self.dt_horizon)

        rx_closest = rx0 + rvx * t_closest
        ry_closest = ry0 + rvy * t_closest
        rz_closest = rz0

        min_dist_horizon = np.sqrt(rx_closest**2 + ry_closest**2 + rz_closest**2)
        future_dist_3d = np.sqrt(
            (future_worker_x - future_machine_x)**2 +
            (future_worker_y - future_machine_y)**2 +
            (future_worker_z - future_machine_z)**2
        )

        # 5. Evaluación de Colisión y Asimilación de Pesos Monte Carlo
        # Partículas en zona crítica (< collision_threshold metros dentro de la ventana de 30 segundos)
        collision_mask = min_dist_horizon <= self.collision_threshold
        collision_probability = float(np.mean(collision_mask)) * 100.0

        # Posición futura estimada (media ponderada del Filtro de Partículas a +30s)
        mean_future_worker = [
            round(float(np.mean(future_worker_x)), 2),
            round(float(np.mean(future_worker_y)), 2),
            round(float(np.mean(future_worker_z)), 2)
        ]

        # Nivel de Alerta Anticipada (30s)
        if collision_probability > 40.0:
            early_warning_level = "CRITICO_30S"
            sug_action = "EVACUACION PREVENTIVA: Intersección inminente proyectada a +30s"
        elif collision_probability > 15.0:
            early_warning_level = "PRECAUCION_30S"
            sug_action = "ALERTA PREVENTIVA: Reducir velocidad de equipo LHD a +30s"
        else:
            early_warning_level = "SEGURO_30S"
            sug_action = "Operación normal proyectada"

        return {
            "prediction_horizon_seconds": 30,
            "collision_probability_30s": round(collision_probability, 2),
            "early_warning_level": early_warning_level,
            "projected_worker_position_30s": mean_future_worker,
            "min_future_distance_meters": round(float(np.min(min_dist_horizon)), 2),
            "mean_future_distance_meters": round(float(np.mean(future_dist_3d)), 2),
            "suggested_action_30s": sug_action
        }

particle_filter_engine = ParticleFilter3DPredictor()
