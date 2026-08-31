import { create } from 'zustand';

interface AlertMessage {
  type?: string;
  timestamp: string;
  alert_id: string | number;
  worker_id: number;
  machine_id: number;
  risk_level: string;
  risk_score: number;
  message: string;
  // Tema 3 Módulos Avanzados
  hmm_state?: string;
  hmm_probabilities?: { SEGURO: number; INCIPIENTE: number; INMINENTE: number };
  particle_filter_30s?: {
    prediction_horizon_seconds: number;
    collision_probability_30s: number;
    early_warning_level: string;
    projected_worker_position_30s: [number, number, number];
    suggested_action_30s: string;
  };
  worker_bpm?: number;
  fatigue_index?: number;
  gas_co_ppm?: number;
  dust_density_mg_m3?: number;
  vibration_rms?: number;
}

interface AlertState {
  alerts: AlertMessage[];
  addAlert: (alert: AlertMessage) => void;
  clearAlerts: () => void;
}

export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  addAlert: (alert) =>
    set((state) => ({
      // Keep only the latest 50 alerts
      alerts: [alert, ...state.alerts].slice(0, 50),
    })),
  clearAlerts: () => set({ alerts: [] }),
}));
