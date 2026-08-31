import numpy as np
from typing import Dict, Any, List, Tuple

class MiningRiskHMM:
    """
    Modelo de Estado Oculto (Hidden Markov Model - HMM) para la Estimación de Riesgo en Minería Subterránea.
    
    Estados Ocultos Latentes (Hidden States):
      - Estado 0: SEGURO (Operación normal, baja interferencia)
      - Estado 1: INCIPIENTE (Advertencia por acercamiento o aumento de biometría/fatiga)
      - Estado 2: INMINENTE (Peligro crítico de colisión / atropello / gas nocivo)
    """

    def __init__(self, n_states: int = 3):
        self.n_states = n_states
        self.state_labels = {0: "SEGURO", 1: "INCIPIENTE", 2: "INMINENTE"}
        
        # Matriz de Transición de Estados A (3x3)
        # P(Estado_t | Estado_t-1)
        self.transition_matrix = np.array([
            [0.85, 0.12, 0.03],  # Desde SEGURO
            [0.20, 0.65, 0.15],  # Desde INCIPIENTE
            [0.05, 0.25, 0.70]   # Desde INMINENTE
        ])
        
        # Distribución de Probabilidad Inicial pi
        self.initial_distribution = np.array([0.70, 0.20, 0.10])
        
        # Medias y Desviaciones de Emisión por Estado (Vector de características: [distance_3d, ttc, bpm, fatigue, gas])
        self.means = np.array([
            [35.0, 45.0, 75.0, 0.15, 8.0],   # Estado 0: SEGURO (Alta distancia, alto TTC, bpm normal, baja fatiga, poco gas)
            [12.0, 12.0, 105.0, 0.45, 25.0],  # Estado 1: INCIPIENTE (Distancia media, bpm elevado, fatiga media)
            [3.0, 3.0, 135.0, 0.80, 65.0]     # Estado 2: INMINENTE (Cerca, bajo TTC, bpm alto, fatiga alta, mucho gas)
        ])
        
        self.stds = np.array([
            [10.0, 15.0, 10.0, 0.10, 5.0],
            [4.0, 4.0, 12.0, 0.12, 10.0],
            [1.5, 1.5, 15.0, 0.10, 20.0]
        ])

    def _emission_probability(self, obs: np.ndarray, state: int) -> float:
        """Calcula la verosimilitud de la observación dado un estado latente bajo distribución Gaussiana Multivariada independiente."""
        mean = self.means[state]
        std = self.stds[state]
        # Evitar división por cero
        std = np.maximum(std, 1e-4)
        prob = np.exp(-0.5 * ((obs - mean) / std) ** 2) / (np.sqrt(2 * np.pi) * std)
        return float(np.prod(prob))

    def estimate_hidden_state(self, telemetry: Dict[str, Any], prev_state_probs: np.ndarray = None) -> Dict[str, Any]:
        """
        Inferencia de Bayes / Algoritmo Forward en tiempo real para obtener el estado oculto actual.
        """
        # Extraer vector de observación [distance_3d, ttc, worker_bpm, fatigue_index, gas_co_ppm]
        dist = float(telemetry.get('distance_3d', 20.0))
        ttc = float(telemetry.get('ttc', 30.0))
        bpm = float(telemetry.get('worker_bpm', 80.0))
        fatigue = float(telemetry.get('fatigue_index', 0.2))
        gas = float(telemetry.get('gas_co_ppm', 10.0))
        
        obs = np.array([dist, ttc, bpm, fatigue, gas])

        if prev_state_probs is None:
            prior = self.initial_distribution
        else:
            prior = np.dot(prev_state_probs, self.transition_matrix)

        # Multiplicar Prior * Emisión
        likelihoods = np.zeros(self.n_states)
        for s in range(self.n_states):
            likelihoods[s] = prior[s] * self._emission_probability(obs, s)

        total = np.sum(likelihoods)
        if total > 0:
            posterior = likelihoods / total
        else:
            posterior = prior

        current_state = int(np.argmax(posterior))

        return {
            "hidden_state_id": current_state,
            "hidden_state_name": self.state_labels[current_state],
            "state_probabilities": {
                "SEGURO": round(float(posterior[0]), 4),
                "INCIPIENTE": round(float(posterior[1]), 4),
                "INMINENTE": round(float(posterior[2]), 4)
            }
        }

hmm_engine = MiningRiskHMM()
