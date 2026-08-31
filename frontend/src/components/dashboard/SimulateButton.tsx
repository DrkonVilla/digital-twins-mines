'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { Play, Loader2, CheckCircle2, AlertCircle, Radio } from 'lucide-react';

interface SimulateButtonProps {
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'destructive';
  size?: 'default' | 'xs' | 'sm' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function SimulateButton({
  variant = 'default',
  size = 'default',
  showLabel = true,
  className = '',
}: SimulateButtonProps) {
  const [loading, setLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [statusText, setStatusText] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  const handleSimulate = async () => {
    try {
      setLoading(true);
      setIsError(false);
      setStatusText('Iniciando simulación...');

      // Call the simulate endpoint in FastAPI backend
      await api.post('/predict/simulate');

      setLoading(false);
      setIsRunning(true);
      setStatusText('Simulando telemetría...');

      // The simulation in backend takes 3 steps * ~2.5s = ~8 seconds
      setTimeout(() => {
        setIsRunning(false);
        setStatusText('Simulación completada');
        setTimeout(() => setStatusText(null), 3000);
      }, 8500);

    } catch (err: any) {
      console.error('Error al ejecutar simulación de telemetría:', err);
      setLoading(false);
      setIsRunning(false);
      setIsError(true);
      setStatusText('Error al conectar con Backend (http://localhost:8000)');
      setTimeout(() => {
        setStatusText(null);
        setIsError(false);
      }, 5000);
    }
  };

  return (
    <div className="inline-flex items-center gap-2">
      <Button
        variant={isRunning ? 'secondary' : variant}
        size={size}
        disabled={loading || isRunning}
        onClick={handleSimulate}
        className={`font-semibold transition-all duration-300 shadow-sm ${
          isRunning ? 'ring-2 ring-emerald-500/50 animate-pulse' : ''
        } ${className}`}
        title="Ejecutar simulador de telemetría en tiempo real (python simulate_live_telemetry.py)"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
        ) : isRunning ? (
          <Radio className="h-4 w-4 text-emerald-500 animate-ping" />
        ) : (
          <Play className="h-4 w-4 text-emerald-400 fill-emerald-400/20" />
        )}

        {showLabel && (
          <span>
            {loading
              ? 'Iniciando...'
              : isRunning
              ? 'Simulando en Vivo...'
              : '⚡ Simular Telemetría'}
          </span>
        )}
      </Button>

      {statusText && (
        <span
          className={`text-xs px-2.5 py-1 rounded-full border flex items-center gap-1.5 backdrop-blur-md transition-all animate-in fade-in zoom-in-95 ${
            isError
              ? 'bg-red-500/10 border-red-500/30 text-red-400 font-medium'
              : isRunning
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 font-medium'
              : 'bg-primary/10 border-primary/30 text-primary font-medium'
          }`}
        >
          {isError ? (
            <AlertCircle className="h-3.5 w-3.5" />
          ) : isRunning ? (
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          ) : (
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
          )}
          {statusText}
        </span>
      )}
    </div>
  );
}
