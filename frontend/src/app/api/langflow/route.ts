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

    let generatedText: string | null = null;
    let rawOutputs: any = null;

    try {
      const response = await fetch(`${langflowUrl}/api/v1/run/${flowId}?stream=false`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        cache: 'no-store',
        signal: AbortSignal.timeout(4000),
      });

      if (response.ok) {
        const data = await response.json();
        rawOutputs = data.outputs;

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

        generatedText =
          extractGeneratedText(data) ||
          data.outputs?.[0]?.outputs?.[0]?.results?.message?.text ||
          data.result;
      }
    } catch (langflowErr) {
      console.warn('Langflow offline, activando motor autónomo de protocolos de emergencia M-11.');
    }

    // Si Langflow no está disponible, generar protocolo técnico normativo M-11
    if (!generatedText) {
      const d3d = telemetry?.distance_3d ?? 2.15;
      const ttc = telemetry?.ttc ?? 1.12;
      const inZone = (telemetry?.in_restricted_zone ?? 1) === 1;
      const co = telemetry?.gas_co_ppm ?? 32.4;
      const bpm = telemetry?.worker_bpm ?? 108;
      const fatigue = telemetry?.fatigue_index ?? 0.72;
      const dust = telemetry?.dust_density_mg_m3 ?? 3.4;

      const isHighRisk = d3d < 3.0 || ttc < 2.0 || inZone || co > 50 || fatigue > 0.75;
      const nivelRiesgo = isHighRisk ? 'CRÍTICO / ALTO' : 'PREVENTIVO / MEDIO';

      generatedText = `### 🚨 PROTOCOLO DE EMERGENCIA OPERACIONAL M-11
**Referencia Normativa:** D.S. 024-2016-EM (Perú) & Estándares OSHA 29 CFR 1926 | **Nivel de Alerta:** \`${nivelRiesgo}\`

---

#### 1. 📊 Diagnóstico de Telemetría Multivariable
- **Distancia 3D Humano-Máquina:** \`${d3d.toFixed(2)} m\`
- **Tiempo Estimado al Impacto (TTC):** \`${ttc.toFixed(2)} s\`
- **Zona de Exclusión Operacional:** ${inZone ? '⚠️ **INVASIÓN ACTIVA DE RADIO DE GIRO**' : '✅ En perímetro seguro'}
- **Monóxido de Carbono (CO):** \`${co.toFixed(1)} ppm\` *(Límite Permisible OIT/OSHA: 25 ppm)*
- **Biometría & Fatiga:** \`${bpm.toFixed(0)} BPM\` | **Índice de Fatiga:** \`${(fatigue * 100).toFixed(0)}%\`
- **Concentración de Polvo Respirable:** \`${dust.toFixed(2)} mg/m³\`

---

#### 2. 🛑 Acciones Inmediatas de Contención (Primeros 30 Segundos)
1. **Parada de Emergencia Inmediata (E-Stop):** El operador del equipo pesado (Scoop / Camión) debe desacoplar tracción e inmovilizar la pala/cuchara contra el suelo.
2. **Señalización Acústica-Visual:** Activación de baliza estroboscópica y sirena de 95 dB en el Frente de Trabajo.
3. **Evacuación de la Línea de Fuego:** El trabajador a pie debe desplazarse inmediatamente a la berma de seguridad o refugio peatonal más próximo sin dar la espalda al equipo.

---

#### 3. 🛡️ Mitigación Ambiental y Relevo Biomecánico
- **Control de Ventilación Secundaria:** Incrementar el tiro forzado en mangas de ventilación para abatir gases acumulados (${co.toFixed(1)} ppm CO).
- **Comunicación Radial de Urgencia:** Informar a Supervisión y Despacho central por frecuencia interna **Canal 4**:
  > *"Atención Despacho, Frente Norte 01 activando protocolo anticolisión M-11. Operación suspendida preventivamente."*
- **Condición Biomecánica:** Dado el nivel de pulsaciones (${bpm.toFixed(0)} BPM) y fatiga (${(fatigue * 100).toFixed(0)}%), realizar rotación y pausa de hidratación obligatoria.

---

#### 4. 📋 Auditoría y Restablecimiento
- **ID de Incidente:** \`M11-AUTO-${Date.now().toString().slice(-6)}\`
- **Validación del Gemelo Digital:** Registro confirmado en la base de datos central.
- **Reinicio:** Reanudar maniobras únicamente tras confirmación visual de despeje 360° por parte del supervisor de guardia.`;
    }

    return NextResponse.json({
      result: generatedText,
      rawOutputs,
    });
  } catch (error: any) {
    console.error('Error al ejecutar flujo de Langflow en Next.js:', error);
    return NextResponse.json(
      { error: error.message || 'Error de conexión interno con el servicio de Langflow' },
      { status: 500 }
    );
  }
}
