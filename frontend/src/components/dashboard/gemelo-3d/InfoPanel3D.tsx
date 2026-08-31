'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Info } from 'lucide-react';
import { SimulateButton } from '@/components/dashboard/SimulateButton';

interface InfoPanelProps {
  activeAlert: any | null;
}

export default function InfoPanel3D({ activeAlert }: InfoPanelProps) {
  const pf = activeAlert?.particle_filter_30s;
  const hmmState = activeAlert?.hmm_state || 'SEGURO';

  return (
    <div className="absolute top-4 right-4 w-96 z-10 pointer-events-none">
      <Card className="bg-card/95 backdrop-blur-md shadow-2xl pointer-events-auto border-primary/20">
        <CardHeader className="pb-2 border-b">
          <CardTitle className="text-base flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Info className="h-5 w-5 text-primary" />
              Gemelo Digital & IA M-11
            </span>
            <Badge variant="outline" className="font-mono text-xs">
              WS EN VIVO
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-3 space-y-3">
          <div className="pt-1 pb-2 border-b border-border/50 flex justify-between items-center">
            <span className="text-xs text-muted-foreground">Prueba de Telemetría:</span>
            <SimulateButton size="xs" variant="secondary" />
          </div>

          {!activeAlert ? (
            <div className="text-xs text-muted-foreground">
              🟢 Monitoreo continuo activo. Parámetros operativos y biométricos en rango normal.
            </div>
          ) : (
            <>
              {/* Nivel de Riesgo ML y HMM */}
              <div className="flex justify-between items-center bg-muted/40 p-2 rounded-lg">
                <div>
                  <span className="text-xs text-muted-foreground block">Riesgo ML (RandomForest):</span>
                  <Badge variant={activeAlert.risk_level === 'ALTO' ? 'destructive' : 'default'} className={activeAlert.risk_level === 'MEDIO' ? 'bg-amber-500 text-black font-bold' : 'font-bold'}>
                    {activeAlert.risk_level} ({activeAlert.risk_score || 0}%)
                  </Badge>
                </div>
                <div className="text-right">
                  <span className="text-xs text-muted-foreground block">Estado Oculto (HMM):</span>
                  <Badge variant={hmmState === 'INMINENTE' ? 'destructive' : hmmState === 'INCIPIENTE' ? 'outline' : 'secondary'} className={hmmState === 'INCIPIENTE' ? 'border-amber-500 text-amber-500 font-bold' : 'font-bold'}>
                    {hmmState}
                  </Badge>
                </div>
              </div>

              {/* Predicción Filtro de Partículas +30s */}
              {pf && (
                <div className="border border-amber-500/40 bg-amber-500/10 p-2 rounded-lg space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold text-amber-500">
                    <span className="flex items-center gap-1">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      Filtro de Partículas (+30s):
                    </span>
                    <span>{pf.collision_probability_30s}% riesgo</span>
                  </div>
                  <p className="text-[11px] text-foreground leading-tight">
                    {pf.suggested_action_30s}
                  </p>
                </div>
              )}

              {/* Telemetría Biométrica y Ambiental */}
              <div className="grid grid-cols-3 gap-1.5 text-[11px] bg-muted/30 p-2 rounded">
                <div>
                  <span className="text-muted-foreground block">Biometría</span>
                  <span className="font-semibold">{activeAlert.worker_bpm ? `${Math.round(activeAlert.worker_bpm)} BPM` : '85 BPM'}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Índice Fatiga</span>
                  <span className={`font-semibold ${(activeAlert.fatigue_index || 0.2) > 0.5 ? 'text-red-500' : 'text-emerald-500'}`}>
                    {(activeAlert.fatigue_index || 0.2).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Gas CO (ppm)</span>
                  <span className="font-semibold">{activeAlert.gas_co_ppm ? `${activeAlert.gas_co_ppm.toFixed(1)} ppm` : '10 ppm'}</span>
                </div>
              </div>

              {/* Mensaje original */}
              <div className="text-[11px] text-muted-foreground border-t pt-1 font-mono">
                {activeAlert.message}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

