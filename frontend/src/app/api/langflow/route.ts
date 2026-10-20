import { NextResponse } from 'next/server';

export interface TelemetryPayload {
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

// Función para obtener la API Key de Gemini desde variables de entorno
function getGeminiApiKey(): string | null {
  if (process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY.trim() !== '') {
    return process.env.GEMINI_API_KEY.trim();
  }
  if (process.env.GOOGLE_API_KEY && process.env.GOOGLE_API_KEY.trim() !== '') {
    return process.env.GOOGLE_API_KEY.trim();
  }
  if (process.env.NEXT_PUBLIC_GEMINI_API_KEY && process.env.NEXT_PUBLIC_GEMINI_API_KEY.trim() !== '') {
    return process.env.NEXT_PUBLIC_GEMINI_API_KEY.trim();
  }
  return null;
}

// Función recursiva para extraer el texto generado de la respuesta de Langflow
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

// Llamada directa a la API de Google Gemini en caso de fallo de Langflow
async function callGeminiApi(apiKey: string, prompt: string): Promise<string | null> {
  const models = ['gemini-2.5-flash', 'gemini-1.5-flash'];
  for (const model of models) {
    try {
      const res = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
              temperature: 0.4,
              maxOutputTokens: 1200,
            },
          }),
          signal: AbortSignal.timeout(6000),
        }
      );
      if (!res.ok) continue;
      const data = await res.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (text && typeof text === 'string' && text.length > 50) {
        return text;
      }
    } catch {
      // Probar siguiente modelo
    }
  }
  return null;
}

// Generador determinista de protocolos de emergencia según D.S. 024-2016-EM y OSHA adaptado dinámicamente
function generateM11SafetyProtocol(telemetry: TelemetryPayload): { text: string; riskLevel: string } {
  const dist = telemetry.distance_3d ?? 25.0;
  const inZone = telemetry.in_restricted_zone !== undefined
    ? Number(telemetry.in_restricted_zone)
    : (dist < 5.0 ? 1 : 0);
  const ttc = telemetry.ttc !== undefined
    ? Number(telemetry.ttc)
    : (dist > 10 ? 99.0 : Number((dist / 2.0).toFixed(2)));
  const workerSpeed = telemetry.worker_speed ?? 1.1;
  const machineSpeed = telemetry.machine_speed ?? 3.8;
  const co = telemetry.gas_co_ppm ?? 9.9;
  const fatigue = telemetry.fatigue_index ?? 0.27;
  const bpm = telemetry.worker_bpm ?? 75.0;
  const dust = telemetry.dust_density_mg_m3 ?? 2.8;

  let riskLevel = 'BAJO';
  let badgeColor = '🟢';
  let statusSummary = 'Condiciones operativas dentro de parámetros de control y tolerancia estándar.';

  if (dist <= 3.5 || (ttc <= 2.0 && ttc > 0) || inZone === 1 || co >= 35.0 || fatigue >= 0.7) {
    riskLevel = 'CRÍTICO (CÓDIGO ROJO)';
    badgeColor = '🚨';
    statusSummary = 'PELIGRO INMINENTE: Interacción hombre-máquina en zona de aplastamiento o condición atmosférica crítica.';
  } else if (dist <= 8.0 || (ttc <= 4.5 && ttc > 0) || co >= 25.0 || fatigue >= 0.5) {
    riskLevel = 'ALTO (CÓDIGO NARANJA)';
    badgeColor = '⚠️';
    statusSummary = 'ALERTA PREVENTIVA: Proximidad de riesgo en rampa subterránea o saturación de monóxido de carbono.';
  } else if (dist <= 15.0 || co >= 15.0 || fatigue >= 0.4) {
    riskLevel = 'MEDIO (CÓDIGO AMARILLO)';
    badgeColor = '🟡';
    statusSummary = 'PRECAUCIÓN OPERACIONAL: Monitoreo activo requerido por proximidad y tránsito de equipo pesado.';
  }

  const triggers: string[] = [];
  if (dist <= 5.0) triggers.push(`**Proximidad Crítica:** Distancia 3D de **${dist.toFixed(1)} m** (Límite seguro: > 10.0 m)`);
  if (ttc <= 3.0 && ttc > 0) triggers.push(`**Tiempo de Choque Inminente (TTC):** **${ttc.toFixed(1)} s** para posible impacto`);
  if (inZone === 1) triggers.push(`**Incursión No Autorizada:** Operario en **Zona Ciega / Radio de Giro Restringido**`);
  if (co >= 25.0) triggers.push(`**Gas Monóxido de Carbono (CO):** **${co.toFixed(1)} ppm** (Supera LMP de 25 ppm según D.S. 024-2016-EM)`);
  if (fatigue >= 0.6) triggers.push(`**Fatiga Operativa Elevada:** Índice **${fatigue.toFixed(2)}** (BPM: **${bpm.toFixed(0)}**)`);
  if (dust >= 3.0) triggers.push(`**Polvo en Suspensión:** **${dust.toFixed(1)} mg/m³** (Visibilidad reducida en socavón)`);
  if (triggers.length === 0) triggers.push(`Todos los sensores registran niveles tolerables en labor.`);

  const now = new Date().toISOString().replace('T', ' ').substring(0, 19);

  const markdown = `
# ${badgeColor} PROTOCOLO DE EMERGENCIA OPERACIONAL M-11
**Referencia:** Gemelo Digital Mina Subterránea | **Timestamp:** \`${now} UTC\`  
**Nivel de Riesgo:** **${riskLevel}**

---

### 1. 🚨 Evaluación de Riesgo Inmediata
- **Diagnóstico Operativo:** ${statusSummary}
- **Nivel de Severidad:** **${riskLevel}**
- **Factores Críticos Detonantes:**
${triggers.map((t) => `  - ${t}`).join('\n')}

**Telemetría de Sensores en Tiempo Real:**
| Sensor / Variable | Valor Actual | Umbral Seguro | Estado Operativo |
| :--- | :--- | :--- | :--- |
| **Distancia 3D** | \`${dist.toFixed(1)} m\` | > 10.0 m | ${dist < 5.0 ? '🔴 CRÍTICO' : dist < 10.0 ? '🟡 ALERTA' : '🟢 NORMAL'} |
| **TTC (Time to Collision)** | \`${ttc >= 60 ? '> 30 s' : `${ttc.toFixed(1)} s`}\` | > 5.0 s | ${ttc < 3.0 && ttc > 0 ? '🔴 INMINENTE' : ttc < 5.0 && ttc > 0 ? '🟡 PRECAUCIÓN' : '🟢 SEGURO'} |
| **Monóxido de Carbono (CO)** | \`${co.toFixed(1)} ppm\` | ≤ 25 ppm (LMP) | ${co > 25.0 ? '🔴 TÓXICO' : '🟢 SEGURO'} |
| **Zona Restringida** | \`${inZone === 1 ? 'SÍ (Incursión)' : 'NO'}\` | Libre | ${inZone === 1 ? '🔴 VIOLACIÓN' : '🟢 DESPEJADO'} |
| **Índice de Fatiga / BPM** | \`${fatigue.toFixed(2)} / ${bpm.toFixed(0)} BPM\` | < 0.50 / < 100 BPM | ${fatigue > 0.6 ? '🔴 FATIGA ALTA' : '🟢 NORMAL'} |
| **Velocidad Maquinaria** | \`${machineSpeed.toFixed(1)} m/s\` | ≤ 4.0 m/s | ${machineSpeed > 4.0 ? '🟡 VELOCIDAD ALTA' : '🟢 NORMAL'} |

---

### 2. 🚧 Acciones Inmediatas para la Maquinaria Pesada (Scooptram / Dumper)
${dist <= 5.0 || inZone === 1 ? `
1. **Frenado y Parada de Emergencia:**
   - Accionar el **Paro de Emergencia (E-Stop)** del equipo de inmediato.
   - Aplicar el freno de parqueo y bloqueo hidráulico de implementos (cuchara/tolva apoyada contra el piso).
2. **Corte de Inercia y Señalización:**
   - Desacoplar la transmisión y cortar la aceleración del motor.
   - Activar luces estroboscópicas de advertencia de 360° y señal acústica de bloqueo.
3. **Restricción de Maniobra:**
   - Queda estrictamente prohibido dar marcha atrás o pivotar hasta confirmar el despeje visual total del personal.
` : `
1. **Reducción Preventiva de Velocidad:**
   - Disminuir velocidad a menos de 5 km/h en galerías y cruces de rampa.
2. **Confirmación Acústica y Radial:**
   - Emitir dos toques de bocina reglamentarios antes de ingresar a curvas ciegas o cruces de personal.
`}

---

### 3. 🏃‍♂️ Protocolo de Evacuación y Protección del Personal
${dist <= 8.0 || inZone === 1 || co >= 25.0 ? `
1. **Salida Inmediata de la Línea de Fuego:**
   - El operario debe replegarse hacia el nicho de seguridad o refugio peatonal más cercano (distancia mínima de 15 m).
2. **Protección Atmosférica y Respiratoria:**
   ${co >= 25.0 ? `- ⚠️ **ALERTA DE GAS CO (${co.toFixed(1)} ppm):** Colocarse de inmediato el **Autorescatador (W-65 o circuito cerrado)**. Evacuar por la chimenea o manga de ventilación hacia aire fresco.` : `- Atmósfera con CO dentro de márgenes. Mantener activo el detector de gas multigas portátil.`}
3. **Gestión de Fatiga y Signos Vitales:**
   ${fatigue >= 0.6 ? `- Con un índice de fatiga de **${fatigue.toFixed(2)}** y ritmo cardíaco de **${bpm.toFixed(0)} BPM**, el trabajador debe suspender su labor de inmediato y ser derivado al tópico médico.` : `- Continuar labores con vigilancia del compañero (sistema partner).`}
` : `
1. **Tránsito Exclusivo por Vía Peatonal:**
   - Caminar únicamente por la berma señalizada con cinta reflectiva.
2. **Contacto Visual con el Operador:**
   - Realizar contacto visual y señal luminosa con la lámpara de casco minero antes de aproximarse al equipo.
`}

---

### 4. 📋 Normativa Legal y Comunicación de Emergencia
- **Reglamento D.S. 024-2016-EM (Perú):**
  - **Art. 248:** Nichos de seguridad obligatorios cada 30 metros en labores de tránsito con maquinaria rodante.
  - **Art. 102:** Límites Máximos Permisibles (LMP) para gases en socavón (Monóxido de Carbono máx. **25 ppm**).
  - **Art. 250:** Derecho a la paralización de labores ante riesgo grave e inminente no controlado.
- **Normativa OSHA 29 CFR 1926.651 / MSHA 30 CFR 57:**
  - Procedimientos de parada de emergencia, señalización de punto ciego y control de energías peligrosas (LOTO).
- **Canal de Comunicación Inmediata:**
  - Notificar de inmediato al **Centro de Control y Despacho Minero (Canal Radial 1 - Emergencias)** indicando nivel **${riskLevel}**, ubicación exacta de la labor y equipo involucrado.
`.trim();

  return { text: markdown, riskLevel };
}

export async function POST(req: Request) {
  let telemetry: TelemetryPayload = {};
  let message = 'Evaluar riesgo operativo y emitir protocolo de emergencia inmediato para mina subterránea.';

  try {
    const body = await req.json();
    if (body.telemetry) telemetry = body.telemetry;
    if (body.message) message = body.message;
  } catch {
    // Si el body está vacío o mal formado, usamos los valores por defecto
  }

  const langflowUrl = process.env.LANGFLOW_URL || 'http://localhost:7860';
  const flowId = process.env.LANGFLOW_FLOW_ID || 'f5dcbe0a-23ce-405a-9c19-d721ad628468';
  const apiKey = process.env.LANGFLOW_API_KEY;

  // 1. INTENTO 1: Consultar Langflow si está activo
  try {
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
      tweaks['CustomComponent-MiningPredictor'] = cleanTelemetry;
      tweaks['MiningRiskPredictor'] = cleanTelemetry;
    }

    const payload = {
      input_value: message || 'Evaluar riesgo operativo y emitir protocolo de emergencia inmediato para mina subterránea.',
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

    // Timeout de 3 segundos para Langflow para evitar bloqueos
    const response = await fetch(`${langflowUrl}/api/v1/run/${flowId}?stream=false`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      cache: 'no-store',
      signal: AbortSignal.timeout(3000),
    });

    if (response.ok) {
      const data = await response.json();
      const generatedText =
        extractGeneratedText(data) ||
        data.outputs?.[0]?.outputs?.[0]?.results?.message?.text ||
        data.result;

      if (generatedText && typeof generatedText === 'string') {
        return NextResponse.json({
          result: generatedText,
          source: 'langflow',
          fallback: false,
          rawOutputs: data.outputs,
        });
      }
    }
  } catch {
    // Servidor Langflow no disponible o tiempo agotado -> Continuar al motor de contingencia
  }

  // 2. INTENTO 2 (Fallback IA): Intentar llamada directa a Google Gemini si hay API Key disponible
  const geminiKey = getGeminiApiKey();
  if (geminiKey) {
    try {
      const dist = telemetry.distance_3d ?? 25.0;
      const ttc = telemetry.ttc !== undefined ? Number(telemetry.ttc) : (dist > 10 ? 99.0 : Number((dist / 2.0).toFixed(2)));
      const co = telemetry.gas_co_ppm ?? 9.9;
      const inZone = telemetry.in_restricted_zone !== undefined ? Number(telemetry.in_restricted_zone) : (dist < 5.0 ? 1 : 0);
      const fatigue = telemetry.fatigue_index ?? 0.27;
      const bpm = telemetry.worker_bpm ?? 75.0;

      const prompt = `
Eres el Asistente Inteligente de Seguridad y Prevención de Riesgos en Minería Subterránea M-11.
Analiza la siguiente telemetría en tiempo real de una labor minera subterránea y genera un Protocolo de Emergencia Oficial estructurado en Markdown según las normativas D.S. 024-2016-EM (Perú) y OSHA.

TELEMETRÍA ACTUAL:
- Distancia 3D hombre-máquina: ${dist} m
- Tiempo al impacto estimado (TTC): ${ttc} s
- Concentración de Monóxido de Carbono (CO): ${co} ppm
- Ingreso a Zona Restringida / Ciega: ${inZone === 1 ? 'SÍ' : 'NO'}
- Índice de Fatiga del Operador: ${fatigue} (Frecuencia cardíaca: ${bpm} BPM)

ESTRUCTURA OBLIGATORIA DEL PROTOCOLO (en Markdown):
# 🚨 PROTOCOLO DE EMERGENCIA OPERACIONAL M-11
### 1. 🚨 Evaluación de Riesgo Inmediata
### 2. 🚧 Acciones de Maniobra para la Maquinaria Pesada
### 3. 🏃‍♂️ Protocolo de Evacuación y Protección del Personal
### 4. 📋 Normativa Legal Aplicable (D.S. 024-2016-EM / OSHA) y Frecuencia Radial
`.trim();

      const aiText = await callGeminiApi(geminiKey, prompt);
      if (aiText) {
        return NextResponse.json({
          result: aiText,
          source: 'gemini',
          fallback: true,
        });
      }
    } catch {
      // Si la API de Gemini falla (por ejemplo cuota agotada), pasar al generador determinista
    }
  }

  // 3. INTENTO 3 (Motor Determinista Oficial M-11): Generación de alta fidelidad basada en D.S. 024-2016-EM
  const nativeProtocol = generateM11SafetyProtocol(telemetry);
  return NextResponse.json({
    result: nativeProtocol.text,
    source: 'm11-native',
    risk_level: nativeProtocol.riskLevel,
    fallback: true,
  });
}
