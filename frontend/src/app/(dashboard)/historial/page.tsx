'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface AlertLog {
  id: number;
  interaction_id: number;
  alert_level: string;
  message: string;
  status: string;
  created_at: string;
}

export default function HistorialPage() {
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await api.get('/alerts/');
        setAlerts(res.data);
      } catch (err) {
        console.error('Error fetching alerts', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Historial de Eventos</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>Registro Histórico de Alertas de Riesgo</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Cargando datos...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha / Hora</TableHead>
                  <TableHead>Nivel de Riesgo</TableHead>
                  <TableHead>Mensaje</TableHead>
                  <TableHead>Interacción ID</TableHead>
                  <TableHead>Estado</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>{format(new Date(alert.created_at), 'dd/MM/yyyy HH:mm:ss')}</TableCell>
                    <TableCell>
                      <Badge variant={alert.alert_level === 'ALTO' ? 'destructive' : 'default'} className={alert.alert_level === 'MEDIO' ? 'bg-amber-500 text-black' : ''}>
                        {alert.alert_level}
                      </Badge>
                    </TableCell>
                    <TableCell>{alert.message}</TableCell>
                    <TableCell>#{alert.interaction_id}</TableCell>
                    <TableCell>{alert.status}</TableCell>
                  </TableRow>
                ))}
                {alerts.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-4">No hay eventos registrados.</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
