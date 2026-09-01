'use client';

import { useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAlertStore } from '@/store/alertStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { AlertTriangle, ShieldAlert, Cpu, Activity, Clock, HeartPulse, Gauge, Wind } from 'lucide-react';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/alerts/ws';

export default function AlertasPage() {
  const alerts = useAlertStore((state) => state.alerts);
  const addAlert = useAlertStore((state) => state.addAlert);

  const handleNewAlert = useCallback((data: any) => {
    addAlert(data);
  }, [addAlert]);

  useWebSocket(WS_URL, handleNewAlert);

  const getRiskInfo = (score: number) => {
    const rawScore = score > 1 ? score : score * 100;
    const formattedScore = rawScore.toFixed(1);
    if (rawScore >= 80) {
      return {
        level: 'ALTO',
        score: formattedScore,
        badgeClass: 'bg-red-600 hover:bg-red-700 text-white font-bold px-2.5 py-0.5 shadow-sm',
        borderClass: 'border-l-red-600',
        iconClass: 'text-red-600',
        bgBox: 'bg-red-500/10 border-red-500/30'
      };
    }
    if (rawScore >= 50) {
      return {
        level: 'MEDIO',
        score: formattedScore,
        badgeClass: 'bg-amber-500 hover:bg-amber-600 text-black font-bold px-2.5 py-0.5 shadow-sm',
        borderClass: 'border-l-amber-500',
        iconClass: 'text-amber-500',
        bgBox: 'bg-amber-500/10 border-amber-500/30'
      };
    }
    return {
      level: 'BAJO',
      score: formattedScore,
      badgeClass: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-2.5 py-0.5 shadow-sm',
      borderClass: 'border-l-emerald-600',
      iconClass: 'text-emerald-500',
      bgBox: 'bg-emerald-500/10 border-emerald-500/30'
    };
  };

  const getHmmBadge = (hmmState: string) => {
    switch (hmmState) {
      case 'INMINENTE':
        return <Badge className="bg-red-600 hover:bg-red-700 text-white font-bold px-2.5 py-0.5 shadow-sm">🔴 INMINENTE</Badge>;
      case 'INCIPIENTE':
        return <Badge className="bg-amber-500 hover:bg-amber-600 text-black font-bold px-2.5 py-0.5 shadow-sm">🟡 INCIPIENTE</Badge>;
      default:
        return <Badge className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-2.5 py-0.5 shadow-sm">🟢 SEGURO</Badge>;
    }
  };

  const getPfBadge = (pfLevel?: string, prob: number = 0) => {
    const level = pfLevel || (prob > 40 ? 'CRITICO_30S' : prob > 15 ? 'PRECAUCION_30S' : 'SEGURO_30S');
    switch (level) {
      case 'CRITICO_30S':
        return <Badge className="bg-red-600 hover:bg-red-700 text-white font-bold px-2.5 py-0.5 shadow-sm">🔴 CRÍTICO (+30s)</Badge>;
      case 'PRECAUCION_30S':
        return <Badge className="bg-amber-500 hover:bg-amber-600 text-black font-bold px-2.5 py-0.5 shadow-sm">🟡 PRECAUCIÓN (+30s)</Badge>;
      default:
        return <Badge className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-2.5 py-0.5 shadow-sm">🟢 SEGURO (+30s)</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Feed de Alertas Predictivas M-11</h2>
          <p className="text-sm text-muted-foreground">Monitoreo multinivel en tiempo real: ML (RF/XGB) + HMM + Particle Filter</p>
        </div>
      </div>
      
      <div className="grid gap-4">
        {alerts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-[350px] text-muted-foreground">
              <ShieldAlert className="h-16 w-16 mb-4 text-muted/50" />
              <p className="text-base font-semibold">Esperando alertas en tiempo real...</p>
              <p className="text-sm text-muted-foreground">El Gemelo Digital M-11 está activo y monitoreando telemetría.</p>
            </CardContent>
          </Card>
        ) : (
          alerts.map((alert, idx) => {
            const riskInfo = getRiskInfo(alert.risk_score || 0);
            const pf = alert.particle_filter_30s;
            const hmmState = alert.hmm_state || 'SEGURO';
            const pfLevel = pf?.early_warning_level;
            const pfProb = pf?.collision_probability_30s ?? 0;

            return (
              <Card key={`${alert.alert_id}-${idx}`} className={`border-l-4 shadow-md hover:shadow-lg transition-all ${riskInfo.borderClass}`}>
                <CardHeader className="pb-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <CardTitle className="text-lg flex items-center gap-2 font-bold">
                      <AlertTriangle className={`h-5 w-5 ${riskInfo.iconClass}`} />
                      {alert.message || 'Alerta de Proximidad Operativa'}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-xs bg-background">
                        Trabajador #{alert.worker_id} ↔ Máquina #{alert.machine_id}
                      </Badge>
                      <Badge variant="outline" className="font-mono text-xs">
                        Distancia: {alert.distance != null ? `${alert.distance}m` : 'N/A'}
                      </Badge>
                    </div>
                  </div>
                  <CardDescription className="text-xs">
                    {format(new Date(alert.timestamp || Date.now()), 'dd/MM/yyyy HH:mm:ss')}
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4 pt-2">
                  {/* Bloques del Modelo Predictivo (3 Badges Diferenciados) */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    
                    {/* 1. Clasificador ML (Random Forest / XGBoost) */}
                    <div className={`p-3 rounded-lg border flex flex-col justify-between ${riskInfo.bgBox}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold flex items-center gap-1.5 text-foreground">
                          <Cpu className="h-4 w-4 text-primary" />
                          Riesgo ML (RF/XGB)
                        </span>
                        <Badge className={riskInfo.badgeClass}>
                          {riskInfo.level}
                        </Badge>
                      </div>
                      <div className="mt-2">
                        <span className="text-2xl font-black tracking-tight">{riskInfo.score}%</span>
                        <span className="text-xs text-muted-foreground block font-medium">Confianza del Clasificador</span>
                      </div>
                    </div>

                    {/* 2. Estado Latente (HMM) */}
                    <div className="bg-muted/40 p-3 rounded-lg border flex flex-col justify-between">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold flex items-center gap-1.5 text-foreground">
                          <Activity className="h-4 w-4 text-primary" />
                          Estado Latente (HMM)
                        </span>
                        {getHmmBadge(hmmState)}
                      </div>
                      <div className="mt-2">
                        <span className="text-lg font-bold text-foreground">{hmmState}</span>
                        <span className="text-xs text-muted-foreground block font-medium">Modelo Oculto de Markov</span>
                      </div>
                    </div>

                    {/* 3. Filtro de Partículas (+30s) */}
                    <div className="bg-muted/40 p-3 rounded-lg border flex flex-col justify-between">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold flex items-center gap-1.5 text-foreground">
                          <Clock className="h-4 w-4 text-primary" />
                          Particle Filter (+30s)
                        </span>
                        {getPfBadge(pfLevel, pfProb)}
                      </div>
                      <div className="mt-2">
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-black">{pfProb}%</span>
                          <span className="text-xs text-muted-foreground font-medium">prob. colisión</span>
                        </div>
                        <p className="text-[11px] font-medium text-foreground line-clamp-1 mt-1" title={pf?.suggested_action_30s || 'Operación normal proyectada'}>
                          💡 {pf?.suggested_action_30s || 'Operación normal proyectada'}
                        </p>
                      </div>
                    </div>

                  </div>

                  {/* Fila Inferior: Biometría & Sensores Ambientales */}
                  {(alert.worker_bpm || alert.fatigue_index || alert.gas_co_ppm) && (
                    <div className="flex flex-wrap items-center gap-4 text-xs bg-muted/20 p-2.5 rounded-md border text-muted-foreground">
                      <span className="flex items-center gap-1 font-medium">
                        <HeartPulse className="h-3.5 w-3.5 text-red-500" />
                        Ritmo Cardíaco: <strong className="text-foreground">{Math.round(alert.worker_bpm || 80)} BPM</strong>
                      </span>
                      <span className="flex items-center gap-1 font-medium">
                        <Gauge className="h-3.5 w-3.5 text-amber-500" />
                        Índice Fatiga: <strong className="text-foreground font-semibold">{(alert.fatigue_index || 0.15).toFixed(2)}</strong>
                      </span>
                      <span className="flex items-center gap-1 font-medium">
                        <Wind className="h-3.5 w-3.5 text-blue-500" />
                        Gas CO: <strong className="text-foreground font-semibold">{(alert.gas_co_ppm || 8.0).toFixed(1)} ppm</strong>
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
