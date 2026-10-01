import { NextResponse } from 'next/server';

interface TelemetryPayload {
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

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { telemetry, message }: { telemetry?: TelemetryPayload; message?: string } = body;

    const langflowUrl = process.env.LANGFLOW_URL || 'http://localhost:7860';
    const flowId = process.env.LANGFLOW_FLOW_ID || 'f5dcbe0a-23ce-405a-9c19-d721ad628468';
    const apiKey = process.env.LANGFLOW_API_KEY;

    if (!flowId) {
      return NextResponse.json(
        { error: 'LANGFLOW_FLOW_ID no está configurado en el archivo .env.local' },
        { status: 500 }
      );
    }

    // Configurar tweaks si se envían datos dinámicos de telemetría de sensores
    const tweaks: Record<string, any> = {};
    if (telemetry && Object.keys(telemetry).length > 0) {
      const cleanTelemetry: Record<string, any> = {};
      if (telemetry.distance_3d !== undefined) cleanTelemetry.distance_3d = Number(telemetry.distance_3d);
      if (telemetry.ttc !== undefined) cleanTelemetry.ttc = Number(telemetry.ttc);
      if (telemetry.worker_speed !== undefined) cleanTelemetry.worker_speed = Number(telemetry.worker_speed);
      if (telemetry.machine_speed !== undefined) cleanTelemetry.machine_speed = Number(telemetry.machine_speed);
      if (telemetry.in_restricted_zone !== undefined) cleanTelemetry.in_restricted_zone = Number(telemetry.in_restricted_zone);
      if (telemetry.gas_co_ppm !== undefined) cleanTelemetry.gas_co_ppm = Number(telemetry.gas_co_ppm);
      if (telemetry.fatigue_index !== undefined) cleanTelemetry.fatigue_index = Number(telemetry.fatigue_index);
      if (telemetry.worker_bpm !== undefined) cleanTelemetry.worker_bpm = Number(telemetry.worker_bpm);
      if (telemetry.dust_density_mg_m3 !== undefined) cleanTelemetry.dust_density_mg_m3 = Number(telemetry.dust_density_mg_m3);

      tweaks['CustomComponent-s7DBd'] = cleanTelemetry;
      tweaks['MiningRiskPredictor'] = cleanTelemetry;
    }

    const payload = {
      input_value: message || 'Generar protocolo de seguridad para la telemetría actual.',
      input_type: 'chat',
      output_type: 'chat',
      ...(Object.keys(tweaks).length > 0 ? { tweaks } : {}),
    };

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (apiKey) {
      headers['x-api-key'] = apiKey;
    }

    const response = await fetch(`${langflowUrl}/api/v1/run/${flowId}?stream=false`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      cache: 'no-store',
    });

    if (!response.ok) {
      const errText = await response.text();
      return NextResponse.json(
        { error: `Error desde servidor Langflow (${response.status}): ${errText}` },
        { status: response.status }
      );
    }

    const data = await response.json();

    // Función recursiva para extraer el mensaje de texto principal generado por el LLM
    function extractGeneratedText(obj: any): string | null {
      if (!obj) return null;
      if (typeof obj === 'object') {
        if (typeof obj.text === 'string' && obj.text.length > 20) {
          return obj.text;
        }
        for (const key of Object.keys(obj)) {
          const res = extractGeneratedText(obj[key]);
          if (res) return res;
        }
      } else if (Array.isArray(obj)) {
        for (const item of obj) {
          const res = extractGeneratedText(item);
          if (res) return res;
        }
      }
      return null;
    }

    const generatedText =
      extractGeneratedText(data) ||
      data.outputs?.[0]?.outputs?.[0]?.results?.message?.text ||
      data.result ||
      'Protocolo generado con éxito.';

    return NextResponse.json({
      result: generatedText,
      rawOutputs: data.outputs,
    });
  } catch (error: any) {
    console.error('Error al ejecutar flujo de Langflow en Next.js:', error);
    return NextResponse.json(
      { error: error.message || 'Error de conexión interno con el servicio de Langflow' },
      { status: 500 }
    );
  }
}
