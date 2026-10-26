import os
import re
import logging
from dotenv import load_dotenv
from app.core.config import settings

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

# Modelos actuales de Google Gemini en LangChain
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class GeminiService:
    """Motor de Inteligencia Artificial para el sistema M-11 impulsado por LangChain."""

    def __init__(self):
        self._cached_key = None
        self._llm = None
        self._chat_chain = None
        self._alert_chain = None

        # Plantilla de Prompt para Chat conversacional con el operador
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres M-11 AI, un asistente de inteligencia artificial experto en seguridad y prevención de riesgos en minería subterránea. "
                "Responde de forma clara, técnica, precisa y concisa a las consultas de los operadores mineros, "
                "haciendo énfasis en protocolos de seguridad operacional, monitoreo de gases tóxicos/asfixiantes (CO, NO2, CH4, O2), fatiga del personal, "
                "zonas de exclusión de maquinaria pesada y respuesta a emergencias. Responde en el mismo idioma en que te hablen."
            )),
            ("human", "{user_message}")
        ])

        # Plantilla de Prompt para Análisis de Alertas operacionales
        self.alert_prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en seguridad minera subterránea. Responde estrictamente en formato Markdown bien estructurado."),
            ("human", (
                "Analiza la siguiente alerta registrada por el sistema M-11:\n\n"
                "- **Nivel de Riesgo**: {alert_level}\n"
                "- **Mensaje Original**: {message}\n"
                "- **Fecha y Hora**: {created_at}\n\n"
                "Responde en formato Markdown con las siguientes secciones:\n"
                "## Evaluación de la situación\n"
                "## Causas probables\n"
                "## Acciones inmediatas recomendadas\n"
                "## Medidas preventivas a largo plazo"
            ))
        ])

    def _get_api_key(self) -> str:
        load_dotenv(override=False)
        return (os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or "").strip()

    def _get_llm_with_fallbacks(self):
        api_key = self._get_api_key()
        if not api_key:
            return None

        if self._llm is None or self._cached_key != api_key:
            try:
                primary = ChatGoogleGenerativeAI(
                    model=PRIMARY_MODEL,
                    google_api_key=api_key,
                    temperature=0.7
                )
                fallbacks = [
                    ChatGoogleGenerativeAI(
                        model=m,
                        google_api_key=api_key,
                        temperature=0.7
                    ) for m in FALLBACK_MODELS
                ]
                self._llm = primary.with_fallbacks(fallbacks)
                self._cached_key = api_key

                # Compilar cadenas ejecutables de LangChain (LCEL)
                self._chat_chain = self.chat_prompt | self._llm | StrOutputParser()
                self._alert_chain = self.alert_prompt | self._llm | StrOutputParser()
            except Exception as e:
                logger.error(f"Error initializing LangChain LLM: {e}")
                self._llm = None
        return self._llm

    def _format_error(self, e: Exception) -> str:
        msg = str(e)
        if "402" in msg or "prepayment" in msg.lower() or "credits are depleted" in msg.lower():
            return (
                "⚠️ **Créditos agotados en Google AI Studio (Error 402)**\n\n"
                "Los créditos prepagados del proyecto asociado a tu API Key se han agotado.\n\n"
                "**Soluciones:**\n"
                "1. **Recargar créditos**: Ve a [AI Studio Projects](https://ai.studio/projects) para recargar saldo.\n"
                "2. **Usar un proyecto con cuota gratuita**: Crea un nuevo proyecto en [Google AI Studio](https://aistudio.google.com/app/apikey), genera una API Key gratuita y actualízala en `backend/.env`."
            )
        if "400" in msg or "API_KEY_INVALID" in msg or "API key not valid" in msg:
            return (
                "⚠️ **Clave de Gemini API no válida o revocada (Error 400)**\n\n"
                "Google rechazó la API Key configurada (`API_KEY_INVALID`).\n\n"
                "**Pasos para solucionarlo:**\n"
                "1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey) y genera una clave.\n"
                "2. Pégala en el archivo `backend/.env`:\n"
                "   ```env\n"
                "   GEMINI_API_KEY=tu_api_key_aqui\n"
                "   ```\n"
                "3. Vuelve a enviar tu mensaje aquí."
            )
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
            return "⚠️ **Límite de solicitudes alcanzado (429)**: Se ha superado temporalmente la cuota de la API de Gemini. Espera unos momentos antes de volver a consultar."
        return f"⚠️ Error en LangChain / Gemini: {msg}"

class DeterministicSafetyInterlock:
    """Motor de Directivas Mandatorias de Seguridad Operacional (D.S. 024-2016-EM).
    
    Actúa como capa de salvaguarda y directivas mandatorias (Safety Protocol Advisory Engine).
    Garantiza que ninguna recomendación generada por el LLM pueda anular o relajar
    una orden de parada de emergencia, evacuación a refugio o relevo de turno.
    Nota: Genera directivas mandatorias de protocolo operacional; no sustituye el cableado
    físico de relés de parada en el PLC/SCADA de maquinaria.
    """
    @staticmethod
    def evaluate_rules(alert_data: dict) -> dict:
        level = str(alert_data.get("alert_level", "")).upper()
        msg = str(alert_data.get("message", "")).lower()
        hazard = str(alert_data.get("hazard", "")).lower()
        gases = [str(g).lower() for g in alert_data.get("gases_present", [])]

        actions = []
        regulations = []
        lockout_engaged = False

        # Regla 1: Proximidad Crítica / Zona Restringida / Colisión (D.S. 024-2016-EM Art. 272/274)
        is_proximity_hazard = (
            hazard in ["colision_proximidad", "zona_restringida", "punto_ciego_retroceso"]
            or any(w in msg for w in ["zona restringida", "in_restricted_zone", "colisión", "colision", "atropello", "punto ciego"])
            or bool(re.search(r"\b(ttc|distancia|proximidad)\b", msg))
        )
        if is_proximity_hazard and level in ["ALTO", "CRITICO"]:
            lockout_engaged = True
            actions.append("PARADA DE EMERGENCIA INMEDIATA: Desconexión de energía motriz del equipo LHD/Scoop (Art. 272 D.S. 024-2016-EM).")
            actions.append("INMOVILIZACIÓN MECÁNICA: Accionamiento de frenos de parqueo y traba de articulación central.")
            regulations.append("D.S. 024-2016-EM Art. 272 / Art. 274 (Zonas de Exclusión)")

        # Regla 2: Gases Asfixiantes / Tóxicos (Monóxido de Carbono CO) (Art. 103/252)
        # Uso estricto de \b para evitar falsos positivos con "colisión", "correcto", etc.
        is_gas_hazard = (
            hazard in ["gas_co", "gas", "combinado_gas_fatiga"]
            or "co" in gases
            or bool(re.search(r"\b(co|gas|gases|monóxido|monoxido|ppm)\b", msg))
        )
        if is_gas_hazard and level in ["MEDIO", "ALTO", "CRITICO"]:
            lockout_engaged = True
            actions.append("EVACUACIÓN INMEDIATA A REFUGIO MINERO hacia labor con ventilación forzada en tiro positivo (Art. 252).")
            actions.append("ACTIVACIÓN DE VENTILACIÓN SECUNDARIA AUXILIAR al 100 % de capacidad.")
            regulations.append("D.S. 024-2016-EM Art. 103 / Art. 252 (LMP CO 25 ppm)")

        # Regla 3: Fatiga Crítica del Personal (Art. 138)
        is_fatigue_hazard = (
            hazard in ["fatiga_operador", "combinado_gas_fatiga"]
            or bool(re.search(r"\b(fatiga|bpm|somnolencia|cardíaco|cardiaco|sueño)\b", msg))
        )
        if is_fatigue_hazard and level in ["MEDIO", "ALTO", "CRITICO"]:
            actions.append("RELEVO OBLIGATORIO DE TURNO: Suspensión preventiva de operación manual de maquinaria pesada.")
            regulations.append("D.S. 024-2016-EM Art. 138 (Control de Fatiga y Turnos)")

        # Regla 4: Falla Mecánica Catastrófica (Art. 367/368)
        is_mech_hazard = (
            hazard in ["falla_maquina", "falla_mecanica"]
            or bool(re.search(r"\b(vibración|vibracion|falla mecánica|falla mecanica|temperatura motor)\b", msg))
        )
        if is_mech_hazard and level in ["ALTO", "CRITICO"]:
            lockout_engaged = True
            actions.append("PARADA DE MOTOR Y BLOQUEO LOTO: Prohibición de arranque hasta inspección mecánica certificada.")
            regulations.append("D.S. 024-2016-EM Art. 367 / Art. 368 (Mantenimiento Mecánico y LOTO)")

        if not actions:
            actions.append("Monitoreo visual continuo y verificación de distanciamiento mínimo de 3 metros en galería.")
            regulations.append("Procedimiento Escrito de Trabajo Seguro (PETS)")

        return {
            "safety_lockout_active": lockout_engaged,
            "deterministic_mandates": actions,
            "normative_references": regulations,
            "override_allowed_by_llm": False,
            "requires_supervisor_signoff": True
        }


    async def analyze_alert(self, alert_data: dict) -> str:
        """Analiza un evento de alerta aplicando PRIMERO las barreras deterministas duras y luego la asistencia LLM."""
        # 1. Evaluación de barrera determinista independiente del LLM (FON-12 / H12)
        interlock = DeterministicSafetyInterlock.evaluate_rules(alert_data)
        
        mandatory_block = "## 🛡️ Protocolo de Seguridad Determinista (D.S. 024-2016-EM)\n\n"
        if interlock["safety_lockout_active"]:
            mandatory_block += "**⚠️ BLOQUEO CRÍTICO DE SEGURIDAD (SAFETY LOCKOUT ACTIVADO)**\n\n"
        
        mandatory_block += "### Directivas Obligatorias Inmediatas:\n"
        for act in interlock["deterministic_mandates"]:
            mandatory_block += f"- {act}\n"
            
        mandatory_block += "\n### Referencias Normativas Aplicables:\n"
        for reg in interlock["normative_references"]:
            mandatory_block += f"- `{reg}`\n"
            
        mandatory_block += "\n*Nota de Seguridad: Estas directivas son mandatorias por diseño y no pueden ser anuladas por el modelo de lenguaje.*\n\n---\n\n"

        llm = self._get_llm_with_fallbacks()
        if not llm or not self._alert_chain:
            return (
                mandatory_block +
                "ℹ️ *Análisis complementario de IA generativa no disponible (clave API de Gemini no configurada). "
                "Las directivas deterministas superiores rigen la operación.*"
            )

        try:
            llm_response = await self._alert_chain.ainvoke({
                "alert_level": alert_data.get("alert_level", "UNKNOWN"),
                "message": alert_data.get("message", "Sin descripción"),
                "created_at": str(alert_data.get("created_at", "N/A"))
            })
            return mandatory_block + "## 🤖 Asistencia Complementaria de IA Generativa\n\n" + llm_response
        except Exception as e:
            logger.error(f"Error in LangChain analyze_alert: {e}")
            return mandatory_block + f"⚠️ *Error consultando el servicio Gemini: {e}*"


    async def chat(self, user_message: str) -> str:
        """Procesa una consulta del operador a través de la cadena LangChain."""
        llm = self._get_llm_with_fallbacks()
        if not llm or not self._chat_chain:
            return (
                "⚠️ **Asistente no disponible**\n\n"
                "No se ha configurado la variable `GEMINI_API_KEY` en el archivo `backend/.env`.\n\n"
                "Para activarlo:\n"
                "1. Genera una API Key en [Google AI Studio](https://aistudio.google.com/app/apikey).\n"
                "2. Agrégala en `backend/.env`:\n"
                "   ```env\n"
                "   GEMINI_API_KEY=tu_api_key_aqui\n"
                "   ```"
            )

        try:
            response = await self._chat_chain.ainvoke({
                "user_message": user_message
            })
            return response
        except Exception as e:
            logger.error(f"Error in LangChain chat: {e}")
            return self._format_error(e)

gemini_service = GeminiService()
