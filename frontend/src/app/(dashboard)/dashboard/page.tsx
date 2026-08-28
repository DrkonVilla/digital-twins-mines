'use client';

import { useCallback, useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useAlertStore } from '@/store/alertStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Bell, Users, Truck, AlertTriangle, ShieldCheck } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/alerts/ws';

interface DashboardStats {
  total_workers: number;
  active_machines: number;
  alerts_today_alto: number;
  alerts_today_medio: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_workers: 0,
    active_machines: 0,
    alerts_today_alto: 0,
    alerts_today_medio: 0,
  });
  const [chartData, setChartData] = useState<any[]>([]);

  const alerts = useAlertStore((s) => s.alerts);
  const addAlert = useAlertStore((s) => s.addAlert);

  const handleWsMessage = useCallback(
    (data: any) => addAlert(data),
    [addAlert]
  );
  useWebSocket(WS_URL, handleWsMessage);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [workersRes, machinesRes, alertsRes] = await Promise.all([
          api.get('/workers/'),
          api.get('/machines/'),
          api.get('/alerts/?limit=200'),
        ]);

        const workers = workersRes.data;
        const machines = machinesRes.data;
        const fetchedAlerts: any[] = alertsRes.data;

        // Count machines with OPERATING status
        const activeMachines = machines.filter((m: any) => m.status === 'OPERATING').length;

        // Filter today's alerts
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const todayAlerts = fetchedAlerts.filter(
          (a: any) => new Date(a.created_at) >= today
        );

        setStats({
          total_workers: workers.filter((w: any) => w.is_active).length,
          active_machines: activeMachines,
          alerts_today_alto: todayAlerts.filter((a: any) => a.alert_level === 'ALTO').length,
          alerts_today_medio: todayAlerts.filter((a: any) => a.alert_level === 'MEDIO').length,
        });

        // Build chart: group last 10 alerts by hour
        const hourMap: Record<string, { alto: number; medio: number }> = {};
        fetchedAlerts.slice(0, 50).forEach((a: any) => {
          const hour = format(new Date(a.created_at), 'HH:mm');
          if (!hourMap[hour]) hourMap[hour] = { alto: 0, medio: 0 };
          if (a.alert_level === 'ALTO') hourMap[hour].alto++;
          if (a.alert_level === 'MEDIO') hourMap[hour].medio++;
        });
        const chartArr = Object.entries(hourMap)
          .map(([hour, v]) => ({ hora: hour, ALTO: v.alto, MEDIO: v.medio }))
          .slice(-10);
        setChartData(chartArr.length > 0 ? chartArr : [{ hora: 'Sin datos', ALTO: 0, MEDIO: 0 }]);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
      }
    };
    fetchStats();
  }, []);

  const recentAlerts = alerts.slice(0, 5);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Dashboard General</h2>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trabajadores Activos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_workers}</div>
            <p className="text-xs text-muted-foreground">Personal registrado y activo</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Maquinaria Operando</CardTitle>
            <Truck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active_machines}</div>
            <p className="text-xs text-muted-foreground">Equipos pesados en operación</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas MEDIO Hoy</CardTitle>
            <Activity className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-500">{stats.alerts_today_medio}</div>
            <p className="text-xs text-muted-foreground">Riesgo intermedio detectado</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas ALTO Hoy</CardTitle>
            <Bell className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats.alerts_today_alto}</div>
            <p className="text-xs text-muted-foreground">Requieren atención inmediata</p>
          </CardContent>
        </Card>
      </div>

      {/* Chart + Alert Feed */}
      <div className="grid gap-4 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Tendencia de Riesgo (Historial)</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px] pr-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorAlto" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorMedio" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#eab308" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                <XAxis dataKey="hora" tick={{ fontSize: 11 }} stroke="rgba(255,255,255,0.3)" />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} stroke="rgba(255,255,255,0.3)" />
                <Tooltip
                  contentStyle={{
                    background: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Area type="monotone" dataKey="ALTO" stroke="#ef4444" fill="url(#colorAlto)" strokeWidth={2} />
                <Area type="monotone" dataKey="MEDIO" stroke="#eab308" fill="url(#colorMedio)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Alertas en Vivo
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 overflow-y-auto max-h-[280px]">
            {recentAlerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground">
                <ShieldCheck className="h-10 w-10 mb-2 opacity-40" />
                <p className="text-sm">Sin alertas recientes</p>
              </div>
            ) : (
              recentAlerts.map((alert, i) => (
                <div
                  key={i}
                  className={`flex items-start gap-2 p-2 rounded-lg border ${
                    alert.risk_level === 'ALTO'
                      ? 'border-red-500/30 bg-red-500/5'
                      : 'border-amber-500/30 bg-amber-500/5'
                  }`}
                >
                  <AlertTriangle
                    className={`h-4 w-4 mt-0.5 shrink-0 ${
                      alert.risk_level === 'ALTO' ? 'text-destructive' : 'text-amber-500'
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-foreground truncate">{alert.message || 'Alerta de Proximidad'}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge
                        variant={alert.risk_level === 'ALTO' ? 'destructive' : 'default'}
                        className={`text-[10px] h-4 ${alert.risk_level === 'MEDIO' ? 'bg-amber-500 text-black' : ''}`}
                      >
                        {alert.risk_level}
                      </Badge>
                      <span className="text-[10px] text-muted-foreground">
                        {format(new Date(alert.timestamp), 'HH:mm:ss')}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
