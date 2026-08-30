import os
import time
from typing import List, Literal

# PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Excel
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Word
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# DB
from app.db.session import async_session_maker
from sqlalchemy import select
from app.models.alert import Alert

ReportFormat = Literal["pdf", "excel", "word"]


def _get_alerts_sync(session_maker) -> list:
    """Helper to use in sync context - we'll call this via async."""
    pass


class ReportGenerator:
    def __init__(self, output_dir: str = "reports_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def _fetch_alerts(self, limit: int = 100) -> list:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Alert).order_by(Alert.created_at.desc()).limit(limit)
            )
            return result.scalars().all()

    def _count_levels(self, alerts: list) -> dict:
        return {
            "ALTO": sum(1 for a in alerts if a.alert_level == "ALTO"),
            "MEDIO": sum(1 for a in alerts if a.alert_level == "MEDIO"),
            "BAJO": sum(1 for a in alerts if a.alert_level == "BAJO"),
        }

    # ─── PDF ──────────────────────────────────────────────────────────────────
    async def generate_pdf_report(self) -> str:
        alerts = await self._fetch_alerts()
        counts = self._count_levels(alerts)
        timestamp = int(time.time())
        filename = f"reporte_m11_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Title'],
            textColor=colors.HexColor('#1e293b'), fontSize=20, spaceAfter=4
        )
        heading_style = ParagraphStyle(
            'CustomHeading', parent=styles['Heading2'],
            textColor=colors.HexColor('#334155'), fontSize=13, spaceBefore=12, spaceAfter=6
        )
        normal_style = ParagraphStyle(
            'CustomNormal', parent=styles['Normal'],
            textColor=colors.HexColor('#475569'), fontSize=10, spaceAfter=4
        )

        elements = []

        # ── Header
        elements.append(Paragraph("Sistema M-11 | Alerta Temprana de Riesgo Minero", title_style))
        elements.append(Paragraph("Reporte de Seguridad y Eventos", heading_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94a3b8')))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Generado: {time.strftime('%d/%m/%Y %H:%M:%S')} | Total alertas analizadas: {len(alerts)}", normal_style))
        elements.append(Spacer(1, 16))

        # ── Resumen ejecutivo
        elements.append(Paragraph("Resumen Ejecutivo", heading_style))
        kpi_data = [
            ["Nivel de Riesgo", "Cantidad", "Porcentaje"],
            ["🔴 ALTO", str(counts["ALTO"]), f"{counts['ALTO']/max(len(alerts),1)*100:.1f}%"],
            ["🟡 MEDIO", str(counts["MEDIO"]), f"{counts['MEDIO']/max(len(alerts),1)*100:.1f}%"],
            ["🟢 BAJO", str(counts["BAJO"]), f"{counts['BAJO']/max(len(alerts),1)*100:.1f}%"],
            ["TOTAL", str(len(alerts)), "100%"],
        ]
        kpi_table = Table(kpi_data, colWidths=[8*cm, 4*cm, 4*cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.HexColor('#f8fafc'), colors.HexColor('#f1f5f9')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWHEIGHT', (0, 0), (-1, -1), 22),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 20))

        # ── Detalle de Alertas
        elements.append(Paragraph("Detalle Cronológico de Alertas", heading_style))
        detail_data = [["Fecha / Hora", "Nivel", "Mensaje", "Interacción", "Estado"]]
        for a in alerts:
            level_color = "#dc2626" if a.alert_level == "ALTO" else "#d97706" if a.alert_level == "MEDIO" else "#16a34a"
            detail_data.append([
                a.created_at.strftime("%d/%m/%Y %H:%M"),
                a.alert_level,
                (a.message or "")[:45] + ("..." if len(a.message or "") > 45 else ""),
                f"#{a.interaction_id}",
                a.status or "PENDIENTE",
            ])

        if len(detail_data) > 1:
            detail_table = Table(detail_data, colWidths=[3.5*cm, 2.5*cm, 7*cm, 2.5*cm, 2.5*cm])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
                ('ROWHEIGHT', (0, 0), (-1, -1), 18),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(detail_table)
        else:
            elements.append(Paragraph("No hay alertas registradas.", normal_style))

        doc.build(elements)
        return filepath

    # ─── EXCEL ────────────────────────────────────────────────────────────────
    async def generate_excel_report(self) -> str:
        alerts = await self._fetch_alerts()
        counts = self._count_levels(alerts)
        timestamp = int(time.time())
        filename = f"reporte_m11_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)

        wb = openpyxl.Workbook()

        # ── Hoja 1: Resumen
        ws_summary = wb.active
        ws_summary.title = "Resumen"
        ws_summary.column_dimensions['A'].width = 28
        ws_summary.column_dimensions['B'].width = 18

        header_fill = PatternFill("solid", fgColor="1E40AF")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        alto_fill = PatternFill("solid", fgColor="FEE2E2")
        medio_fill = PatternFill("solid", fgColor="FEF9C3")
        bajo_fill = PatternFill("solid", fgColor="DCFCE7")

        ws_summary['A1'] = "Sistema M-11 — Reporte de Seguridad"
        ws_summary['A1'].font = Font(bold=True, size=16, color="0F172A")
        ws_summary['A2'] = f"Generado: {time.strftime('%d/%m/%Y %H:%M:%S')}"
        ws_summary['A2'].font = Font(italic=True, color="64748B")
        ws_summary['A3'] = f"Total alertas: {len(alerts)}"

        ws_summary.append([])
        ws_summary.append(["Nivel de Riesgo", "Cantidad"])
        for cell in ws_summary[ws_summary.max_row]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        for level, fill in [("ALTO", alto_fill), ("MEDIO", medio_fill), ("BAJO", bajo_fill)]:
            row = ws_summary.max_row + 1
            ws_summary.append([level, counts[level]])
            ws_summary.cell(row, 1).fill = fill
            ws_summary.cell(row, 2).fill = fill
            ws_summary.cell(row, 1).font = Font(bold=True)
            ws_summary.cell(row, 2).alignment = Alignment(horizontal='center')

        # ── Hoja 2: Detalle
        ws_detail = wb.create_sheet("Detalle de Alertas")
        cols = ["ID", "Fecha / Hora", "Nivel de Riesgo", "Mensaje", "Interacción ID", "Estado"]
        ws_detail.append(cols)
        for i, cell in enumerate(ws_detail[1]):
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        widths = [8, 20, 16, 55, 15, 15]
        for i, w in enumerate(widths, 1):
            ws_detail.column_dimensions[ws_detail.cell(1, i).column_letter].width = w

        for a in alerts:
            fill = PatternFill("solid", fgColor="FEE2E2") if a.alert_level == "ALTO" else \
                   PatternFill("solid", fgColor="FEF9C3") if a.alert_level == "MEDIO" else \
                   PatternFill("solid", fgColor="F0FDF4")
            row_data = [
                a.id,
                a.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                a.alert_level,
                a.message or "",
                a.interaction_id,
                a.status or "PENDIENTE",
            ]
            ws_detail.append(row_data)
            for cell in ws_detail[ws_detail.max_row]:
                cell.fill = fill

        wb.save(filepath)
        return filepath

    # ─── WORD ─────────────────────────────────────────────────────────────────
    async def generate_word_report(self) -> str:
        alerts = await self._fetch_alerts()
        counts = self._count_levels(alerts)
        timestamp = int(time.time())
        filename = f"reporte_m11_{timestamp}.docx"
        filepath = os.path.join(self.output_dir, filename)

        doc = Document()

        # Estilos
        style = doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)

        # Título
        title = doc.add_heading("Sistema M-11 — Reporte de Seguridad Minera", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Generado el {time.strftime('%d/%m/%Y a las %H:%M:%S')}")
        doc.add_paragraph()

        # Resumen ejecutivo
        doc.add_heading("Resumen Ejecutivo", 1)
        p = doc.add_paragraph(f"Total de alertas analizadas: ")
        p.add_run(str(len(alerts))).bold = True

        table_s = doc.add_table(rows=4, cols=3)
        table_s.style = 'Table Grid'
        headers = ["Nivel de Riesgo", "Cantidad", "Porcentaje"]
        for i, h in enumerate(headers):
            cell = table_s.cell(0, i)
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            cell._tc.get_or_add_tcPr().append(
                doc.element.makeelement(qn('w:shd'), {'w:fill': '1E40AF', 'w:color': 'auto', 'w:val': 'clear'})
            )

        rows_data = [
            ("ALTO", counts["ALTO"]),
            ("MEDIO", counts["MEDIO"]),
            ("BAJO", counts["BAJO"]),
        ]
        fills = ['DC2626', 'D97706', '16A34A']
        for i, (level, cnt) in enumerate(rows_data):
            row = table_s.rows[i + 1]
            row.cells[0].text = level
            row.cells[1].text = str(cnt)
            row.cells[2].text = f"{cnt/max(len(alerts),1)*100:.1f}%"
            for cell in row.cells:
                cell._tc.get_or_add_tcPr().append(
                    doc.element.makeelement(qn('w:shd'), {'w:fill': fills[i], 'w:color': 'auto', 'w:val': 'clear'})
                )

        doc.add_paragraph()
        doc.add_heading("Detalle Cronológico de Alertas", 1)

        detail_table = doc.add_table(rows=1, cols=5)
        detail_table.style = 'Table Grid'
        hdr_row = detail_table.rows[0].cells
        for i, h in enumerate(["Fecha", "Nivel", "Mensaje", "Interacción", "Estado"]):
            hdr_row[i].text = h
            hdr_row[i].paragraphs[0].runs[0].font.bold = True

        for a in alerts:
            row = detail_table.add_row().cells
            row[0].text = a.created_at.strftime("%d/%m/%Y %H:%M")
            row[1].text = a.alert_level
            row[2].text = (a.message or "")[:60]
            row[3].text = f"#{a.interaction_id}"
            row[4].text = a.status or "PENDIENTE"

        doc.save(filepath)
        return filepath

    async def generate(self, fmt: ReportFormat = "pdf") -> str:
        if fmt == "excel":
            return await self.generate_excel_report()
        elif fmt == "word":
            return await self.generate_word_report()
        else:
            return await self.generate_pdf_report()


report_generator = ReportGenerator()
