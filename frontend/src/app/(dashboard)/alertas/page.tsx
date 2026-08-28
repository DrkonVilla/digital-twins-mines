'use client';

import { useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAlertStore } from '@/store/alertStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/alerts/ws';

export default function AlertasPage() {
  const alerts = useAlertStore((state) => state.alerts);
  const addAlert = useAlertStore((state) => state.addAlert);

  const handleNewAlert = useCallback((data: any) => {
    addAlert(data);
  }, [addAlert]);

  // Connect to the WebSocket
  useWebSocket(WS_URL, handleNewAlert);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Feed de Alertas</h2>
      
      <div className="grid gap-4">
        {alerts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-[400px] text-muted-foreground">
              <ShieldAlert className="h-16 w-16 mb-4 text-muted/50" />
              <p>Esperando alertas en tiempo real...</p>
              <p className="text-sm">Sistema conectado y monitoreando.</p>
            </CardContent>
          </Card>
        ) : (
          alerts.map((alert, idx) => (
            <Card key={`${alert.alert_id}-${idx}`} className={`border-l-4 ${alert.risk_level === 'ALTO' ? 'border-l-destructive' : 'border-l-amber-500'}`}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <AlertTriangle className={alert.risk_level === 'ALTO' ? 'text-destructive' : 'text-amber-500'} />
                    {alert.message || 'Alerta de Proximidad'}
                  </CardTitle>
                  <Badge variant={alert.risk_level === 'ALTO' ? 'destructive' : 'default'} className={alert.risk_level === 'MEDIO' ? 'bg-amber-500 text-black hover:bg-amber-600' : ''}>
                    RIESGO {alert.risk_level}
                  </Badge>
                </div>
                <CardDescription>
                  {format(new Date(alert.timestamp), 'dd/MM/yyyy HH:mm:ss')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm">
                  <p><span className="font-semibold">Trabajador:</span> {alert.worker_id}</p>
                  <p><span className="font-semibold">Maquinaria:</span> {alert.machine_id}</p>
                  <p><span className="font-semibold">Probabilidad (Score):</span> {(alert.risk_score * 100).toFixed(1)}%</p>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
