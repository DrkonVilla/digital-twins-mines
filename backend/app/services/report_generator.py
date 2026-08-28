import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.db.session import async_session_maker
from sqlalchemy import select
from app.models.alert import Alert

class ReportGenerator:
    def __init__(self, output_dir: str = "reports_output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def generate_pdf_report(self) -> str:
        timestamp = int(time.time())
        filename = f"reporte_seguridad_m11_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Título
        elements.append(Paragraph("Reporte de Seguridad y Alertas - M-11", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Fecha de generación: {time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Extraer datos de la base de datos
        async with async_session_maker() as session:
            result = await session.execute(
                select(Alert).order_by(Alert.created_at.desc()).limit(50)
            )
            alerts = result.scalars().all()

        # Resumen Ejecutivo
        alta_riesgo = sum(1 for a in alerts if a.alert_level == "ALTO")
        medio_riesgo = sum(1 for a in alerts if a.alert_level == "MEDIO")
        
        elements.append(Paragraph("Resumen de Alertas Recientes", styles['Heading2']))
        elements.append(Paragraph(f"Total de alertas analizadas: {len(alerts)}", styles['Normal']))
        elements.append(Paragraph(f"Alertas de Riesgo ALTO: {alta_riesgo}", styles['Normal']))
        elements.append(Paragraph(f"Alertas de Riesgo MEDIO: {medio_riesgo}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Tabla de Alertas
        data = [["Fecha", "Nivel", "Interacción ID", "Estado"]]
        for a in alerts:
            data.append([
                a.created_at.strftime("%Y-%m-%d %H:%M"),
                a.alert_level,
                f"#{a.interaction_id}",
                a.status
            ])

        if len(data) > 1:
            table = Table(data, colWidths=[120, 80, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay alertas registradas para mostrar.", styles['Normal']))

        # Construir PDF
        doc.build(elements)
        return filepath

report_generator = ReportGenerator()
