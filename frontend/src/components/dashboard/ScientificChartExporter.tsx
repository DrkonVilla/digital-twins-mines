"use client";

import React, { useState } from 'react';
import { Download, FileText, Image as ImageIcon, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ScientificChartExporterProps {
  /** ID del elemento HTML contenedor del gráfico o canvas SVG */
  containerId: string;
  /** Nombre base para el archivo descargado (sin extensión) */
  baseFilename: string;
  /** Título científico de la figura para la leyenda */
  figureTitle?: string;
}

/**
 * Componente React para exportar gráficos (Recharts, SVG, Canvas o Three.js)
 * a resolución científica de 600 DPI reales (factor de escala 6.25x sobre 96 DPI estándar).
 */
export const ScientificChartExporter: React.FC<ScientificChartExporterProps> = ({
  containerId,
  baseFilename,
  figureTitle = "Figura Científica M-11"
}) => {
  const [exporting, setExporting] = useState(false);

  const exportHighResImage = async (format: 'png' | 'svg') => {
    setExporting(true);
    try {
      const container = document.getElementById(containerId);
      if (!container) {
        throw new Error(`Contenedor #${containerId} no encontrado en el DOM.`);
      }

      // Si se solicita SVG y hay un elemento SVG directo
      const svgElement = container.querySelector('svg');
      if (format === 'svg' && svgElement) {
        const serializer = new XMLSerializer();
        const svgStr = serializer.serializeToString(svgElement);
        const blob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        triggerDownload(url, `${baseFilename}_vectorial.svg`);
        setExporting(false);
        return;
      }

      // Para PNG a 600 DPI: renderizar en canvas offscreen escalado 6.25x
      const scale = 600 / 96; // 6.25 factor multiplicador
      const rect = container.getBoundingClientRect();
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(rect.width * scale);
      canvas.height = Math.round(rect.height * scale);
      const ctx = canvas.getContext('2d');

      if (!ctx) throw new Error("No se pudo inicializar contexto 2D");

      // Fondo blanco para publicación científica
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      if (svgElement) {
        const svgCopy = svgElement.cloneNode(true) as SVGSVGElement;
        svgCopy.setAttribute('width', `${canvas.width}px`);
        svgCopy.setAttribute('height', `${canvas.height}px`);

        const svgData = new XMLSerializer().serializeToString(svgCopy);
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const DOMURL = window.URL || window.webkitURL || window;
        const url = DOMURL.createObjectURL(svgBlob);

        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          DOMURL.revokeObjectURL(url);
          const pngUrl = canvas.toDataURL('image/png', 1.0);
          triggerDownload(pngUrl, `${baseFilename}_600dpi.png`);
          setExporting(false);
        };
        img.onerror = () => {
          setExporting(false);
        };
        img.src = url;
      } else {
        // En caso de canvas Three.js WebGL
        const webglCanvas = container.querySelector('canvas');
        if (webglCanvas) {
          ctx.drawImage(webglCanvas, 0, 0, canvas.width, canvas.height);
          const pngUrl = canvas.toDataURL('image/png', 1.0);
          triggerDownload(pngUrl, `${baseFilename}_600dpi.png`);
          setExporting(false);
        } else {
          setExporting(false);
        }
      }
    } catch (err) {
      console.error("Error al exportar gráfico en alta resolución:", err);
      setExporting(false);
    }
  };

  const triggerDownload = (url: string, filename: string) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-zinc-800/60">
      <span className="text-xs text-zinc-400 font-medium mr-auto">
        {figureTitle} (Estándar Revista Q1/Q2):
      </span>
      <Button
        variant="outline"
        size="sm"
        disabled={exporting}
        onClick={() => exportHighResImage('png')}
        className="text-xs h-7 gap-1.5 border-zinc-700 bg-zinc-900/60 text-zinc-200 hover:bg-zinc-800"
      >
        {exporting ? <Loader2 className="w-3 h-3 animate-spin" /> : <ImageIcon className="w-3 h-3 text-red-400" />}
        <span>PNG 600 DPI</span>
      </Button>
      <Button
        variant="outline"
        size="sm"
        disabled={exporting}
        onClick={() => exportHighResImage('svg')}
        className="text-xs h-7 gap-1.5 border-zinc-700 bg-zinc-900/60 text-zinc-200 hover:bg-zinc-800"
      >
        <FileText className="w-3 h-3 text-blue-400" />
        <span>Vectorial SVG</span>
      </Button>
    </div>
  );
};
