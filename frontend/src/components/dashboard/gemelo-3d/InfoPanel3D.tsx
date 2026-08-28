'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Info } from 'lucide-react';

interface InfoPanelProps {
  activeAlert: any | null;
}

export default function InfoPanel3D({ activeAlert }: InfoPanelProps) {
  return (
    <div className="absolute top-4 right-4 w-80 z-10 pointer-events-none">
      <Card className="bg-card/90 backdrop-blur-sm shadow-xl pointer-events-auto">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <Info className="h-5 w-5 text-primary" />
            Estado del Entorno
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!activeAlert ? (
            <div className="text-sm text-muted-foreground">
              Sin alertas recientes. El área opera bajo parámetros normales.
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold">Alerta Activa:</span>
                <Badge variant={activeAlert.risk_level === 'ALTO' ? 'destructive' : 'default'} className={activeAlert.risk_level === 'MEDIO' ? 'bg-amber-500 text-black' : ''}>
                  {activeAlert.risk_level}
                </Badge>
              </div>
              <div className="text-sm bg-muted/50 p-2 rounded">
                <p className="flex items-start gap-2 text-foreground">
                  {activeAlert.risk_level === 'ALTO' && <AlertTriangle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />}
                  {activeAlert.message}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-muted-foreground block">Trabajador</span>
                  <span className="font-mono">W-00{activeAlert.worker_id}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Máquina</span>
                  <span className="font-mono">M-00{activeAlert.machine_id}</span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
