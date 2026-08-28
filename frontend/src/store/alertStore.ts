import { create } from 'zustand';

interface AlertMessage {
  type: string;
  timestamp: string;
  alert_id: string;
  worker_id: number;
  machine_id: number;
  risk_level: string;
  risk_score: number;
  message: string;
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
