# services/pdf_report.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import tempfile, os

def make_pdf(user, data):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle", parent=styles["Title"],
        alignment=1, textColor=colors.HexColor("#1F4E79"), spaceAfter=20
    )
    heading_style = ParagraphStyle(
        name="HeadingStyle", parent=styles["Heading2"],
        textColor=colors.HexColor("#2E75B6"), spaceAfter=10
    )
    subhead_style = ParagraphStyle(
        name="SubheadStyle", parent=styles["Heading3"],
        textColor=colors.HexColor("#385723"), spaceAfter=8
    )

    story = []

    story.append(Paragraph("Content Pipeline Report", title_style))
    story.append(Paragraph(f"<b>User:</b> {user}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("1. Uploaded Keywords", heading_style))
    raw_kws = ", ".join(data.get("raw_keywords", []))
    cleaned_kws = ", ".join(data.get("cleaned_keywords", []))
    if not raw_kws: raw_kws = "— No raw keywords found —"
    if not cleaned_kws: cleaned_kws = "— No cleaned keywords found —"

    story.append(Paragraph(f"<b>Raw:</b> {raw_kws}", styles["Normal"]))
    story.append(Paragraph(f"<b>Cleaned:</b> {cleaned_kws}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("2. Keyword Clusters", heading_style))
    clusters = data.get("clusters", {})
    if not clusters:
        story.append(Paragraph("— No clusters available —", styles["Normal"]))
    else:
        for c, words in clusters.items():
            story.append(Paragraph(f"<b>{c}:</b> {', '.join(words)}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("3. Outlines & Post Ideas", heading_style))
    outlines = data.get("outlines", {})
    if not outlines:
        story.append(Paragraph("— No outlines or ideas found —", styles["Normal"]))
    else:
        for c, o in outlines.items():
            story.append(Paragraph(f"<b>{c}</b>", subhead_style))
            story.append(Paragraph(f"<b>Intro:</b> {o.get('intro','')}", styles["Normal"]))
            story.append(Paragraph(f"<b>Sections:</b> {', '.join(o.get('sections',[]))}", styles["Normal"]))
            story.append(Paragraph(f"<b>Conclusion:</b> {o.get('conclusion','')}", styles["Normal"]))
            story.append(Paragraph(f"<b>Idea:</b> {o.get('idea','')}", styles["Normal"]))
            story.append(Spacer(1, 0.25 * inch))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("<b>Report generated automatically by the Content Pipeline Bot.</b>", styles["Italic"]))

    doc.build(story)
    return tmp.name
