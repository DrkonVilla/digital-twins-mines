from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

class GeminiService:
    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except ImportError:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._legacy_model = genai.GenerativeModel('gemini-1.5-pro')

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_alert(self, alert_data: dict) -> str:
        if not self.client and not hasattr(self, '_legacy_model'):
            return "⚠️ No se ha configurado GEMINI_API_KEY. Configure la variable en el archivo `.env` del backend para activar el análisis por IA."

        prompt = f"""
Eres un experto en seguridad minera subterránea. Analiza la siguiente alerta registrada por el sistema M-11:

- **Nivel de Riesgo**: {alert_data.get('alert_level')}
- **Mensaje Original**: {alert_data.get('message')}
- **Fecha y Hora**: {alert_data.get('created_at')}

Responde en formato Markdown con las siguientes secciones:
## Evaluación de la situación
## Causas probables
## Acciones inmediatas recomendadas
## Medidas preventivas a largo plazo
"""
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash', contents=prompt
                )
                return response.text
            else:
                response = await self._legacy_model.generate_content_async(prompt)
                return response.text
        except Exception as e:
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat(self, user_message: str) -> str:
        if not self.client and not hasattr(self, '_legacy_model'):
            return "El asistente de IA no está disponible. Configure GEMINI_API_KEY en el backend."

        prompt = f"""Eres M-11 AI, un experto en seguridad minera subterránea.
Responde a la siguiente consulta de un operador de manera clara y concisa:

Consulta: {user_message}"""
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash', contents=prompt
                )
                return response.text
            else:
                response = await self._legacy_model.generate_content_async(prompt)
                return response.text
        except Exception as e:
            raise e

gemini_service = GeminiService()
