'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  ShieldAlert, 
  Loader2, 
  X, 
  RefreshCw, 
  Copy, 
  Check, 
  AlertTriangle,
  Bot,
  Activity,
  Flame,
  Gauge
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface TelemetryData {
  distance_3d?: number;
  ttc?: number;
  worker_speed?: number;
  machine_speed?: number;
  in_restricted_zone?: number;
  gas_co_ppm?: number;
  fatigue_index?: number;
  worker_bpm?: number;
  dust_density_mg_m3?: number;
}

interface EmergencyProtocolModalProps {
  telemetryData?: TelemetryData;
  buttonLabel?: string;
  buttonVariant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'destructive';
  buttonSize?: 'default' | 'xs' | 'sm' | 'lg';
  className?: string;
}

export function EmergencyProtocolModal({
  telemetryData,
  buttonLabel = 'Consultar Protocolo IA (M-11)',
  buttonVariant = 'destructive',
  buttonSize = 'default',
  className = '',
}: EmergencyProtocolModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [protocol, setProtocol] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Cerrar con tecla Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const fetchProtocol = async () => {
    setLoading(true);
    setErrorMsg(null);
    setIsOpen(true);

    try {
      const res = await fetch('/api/langflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telemetry: telemetryData,
          message: 'Evaluar riesgo operativo y emitir protocolo de emergencia inmediato para mina subterránea.',
        }),
      });

      const data = await res.json();

      if (!res.ok || data.error) {
        throw new Error(data.error || `Error HTTP ${res.status}`);
      }

      setProtocol(data.result);
    } catch (err: any) {
      console.error('Error al invocar Langflow:', err);
      setErrorMsg(err.message || 'No se pudo conectar con el servidor de Langflow.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!protocol) return;
    navigator.clipboard.writeText(protocol);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      <Button
        variant={buttonVariant}
        size={buttonSize}
        onClick={fetchProtocol}
        className={`flex items-center gap-2 font-semibold shadow-md transition-all active:scale-95 ${className}`}
      >
        <ShieldAlert className="w-4 h-4 text-white" />
        <span>{buttonLabel}</span>
      </Button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl overflow-hidden">
            
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/80 bg-zinc-900/60">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-zinc-100 flex items-center gap-2">
                    Protocolo de Emergencia Minera M-11
                    <Badge variant="outline" className="text-xs bg-red-500/10 text-red-400 border-red-500/30">
                      Gemini AI + ML
                    </Badge>
                  </h3>
                  <p className="text-xs text-zinc-400">
                    Inferencia predictiva en tiempo real y normativas D.S. 024-2016-EM / OSHA
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
                title="Cerrar (Esc)"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Telemetry Bar (si hay datos disponibles) */}
            {telemetryData && (
              <div className="px-6 py-2 bg-zinc-900/40 border-b border-zinc-800/60 flex flex-wrap items-center gap-4 text-xs text-zinc-400">
                {telemetryData.distance_3d !== undefined && (
                  <div className="flex items-center gap-1.5">
                    <Gauge className="w-3.5 h-3.5 text-zinc-500" />
                    <span>Distancia 3D:</span>
                    <strong className="text-zinc-200">{telemetryData.distance_3d}m</strong>
                  </div>
                )}
                {telemetryData.ttc !== undefined && (
                  <div className="flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-amber-500" />
                    <span>TTC:</span>
                    <strong className="text-amber-300">{telemetryData.ttc}s</strong>
                  </div>
                )}
                {telemetryData.gas_co_ppm !== undefined && (
                  <div className="flex items-center gap-1.5">
                    <Flame className="w-3.5 h-3.5 text-red-500" />
                    <span>Gas CO:</span>
                    <strong className="text-red-300">{telemetryData.gas_co_ppm} ppm</strong>
                  </div>
                )}
                {telemetryData.fatigue_index !== undefined && (
                  <div className="flex items-center gap-1.5">
                    <Bot className="w-3.5 h-3.5 text-purple-400" />
                    <span>Fatiga:</span>
                    <strong className="text-purple-300">{telemetryData.fatigue_index}</strong>
                  </div>
                )}
              </div>
            )}

            {/* Contenido / Markdown */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 text-zinc-300 text-sm leading-relaxed scrollbar-thin scrollbar-thumb-zinc-700">
              {loading ? (
                <div className="flex flex-col items-center justify-center py-16 gap-3 text-zinc-400">
                  <div className="relative flex items-center justify-center">
                    <Loader2 className="w-10 h-10 animate-spin text-red-500" />
                    <Bot className="w-4 h-4 absolute text-zinc-300" />
                  </div>
                  <p className="font-medium text-zinc-200">
                    Procesando telemetría minera con Langflow...
                  </p>
                  <p className="text-xs text-zinc-500 max-w-sm text-center">
                    Cargando inferencia de XGBoost y consultando protocolos normativos con Google Gemini.
                  </p>
                </div>
              ) : errorMsg ? (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <strong className="font-semibold block">Error al generar protocolo</strong>
                    <p className="text-xs text-red-400/90">{errorMsg}</p>
                    <p className="text-xs text-zinc-400 mt-2">
                      Verifica que el servidor de Langflow esté activo en <code className="text-zinc-300">http://localhost:7860</code> y que el flujo tenga el modelo configurado.
                    </p>
                  </div>
                </div>
              ) : protocol ? (
                <div className="prose prose-invert max-w-none prose-headings:text-zinc-100 prose-headings:font-bold prose-h1:text-xl prose-h2:text-lg prose-h3:text-base prose-strong:text-zinc-100 prose-ul:my-2 prose-li:my-0.5">
                  <ReactMarkdown>{protocol}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-zinc-500 text-center py-12">
                  No hay protocolo generado todavía.
                </p>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-6 py-3 border-t border-zinc-800/80 bg-zinc-900/60">
              <div className="text-xs text-zinc-500">
                Sistema Autónomo de Detección de Riesgos • Gemelo Digital M-11
              </div>

              <div className="flex items-center gap-2">
                {protocol && !loading && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopy}
                    className="border-zinc-700 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-200 gap-1.5"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Copiado</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-zinc-400" />
                        <span>Copiar</span>
                      </>
                    )}
                  </Button>
                )}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchProtocol}
                  disabled={loading}
                  className="border-zinc-700 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-200 gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                  Re-evaluar
                </Button>

                <Button
                  variant="default"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="bg-zinc-700 hover:bg-zinc-600 text-white"
                >
                  Cerrar
                </Button>
              </div>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
