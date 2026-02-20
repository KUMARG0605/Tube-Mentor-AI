"""PDF generator service for creating study notes using ReportLab."""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, ListFlowable, ListItem,
)
from reportlab.lib.enums import TA_CENTER

from app.config import settings


def _get_styles():
    """Create and return custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=HexColor("#1a1a2e"),
        spaceAfter=20,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=HexColor("#e94560"),
        spaceBefore=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        "BodyText2",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        textColor=HexColor("#333333"),
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        "QuizQuestion",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15,
        textColor=HexColor("#0f3460"),
        spaceBefore=12,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    ))

    styles.add(ParagraphStyle(
        "QuizOption",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        leftIndent=20,
        textColor=HexColor("#444444"),
    ))

    styles.add(ParagraphStyle(
        "QuizAnswer",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        leftIndent=20,
        textColor=HexColor("#16a085"),
        fontName="Helvetica-BoldOblique",
    ))

    return styles


def _clean_markdown(text: str) -> str:
    """Convert basic Markdown to ReportLab-compatible markup."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"^#{1,4}\s*", "", text, flags=re.MULTILINE)
    return text


def generate_pdf(
    video_id: str,
    title: str,
    summary_text: str,
    key_topics: list[str],
    questions: list[dict],
) -> str:
    """
    Generate a PDF with summary notes and quiz.
    
    Returns the filename of the generated PDF.
    """
    # Create safe filename
    safe_title = re.sub(r"[^\w\s-]", "", title)[:60].strip()
    file_name = f"{safe_title}_{video_id}.pdf"
    file_path = settings.PDF_DIR / file_name

    # Create document template
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = _get_styles()
    story = []

    # Title and video info
    story.append(Paragraph("TubeMentor AI - Study Notes", styles["CustomTitle"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Video: {title}", styles["SectionHeading"]))
    story.append(Paragraph(
        f"YouTube: https://www.youtube.com/watch?v={video_id}",
        styles["BodyText2"],
    ))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#e94560")))
    story.append(Spacer(1, 10))

    # Key topics section
    if key_topics:
        story.append(Paragraph("Key Topics", styles["SectionHeading"]))
        topic_items = [ListItem(Paragraph(t, styles["BodyText2"])) for t in key_topics]
        story.append(ListFlowable(topic_items, bulletType="bullet", start="•"))
        story.append(Spacer(1, 10))

    # Summary section
    story.append(Paragraph("Detailed Summary", styles["SectionHeading"]))
    for paragraph in summary_text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            story.append(Spacer(1, 4))
            continue
        cleaned = _clean_markdown(paragraph)
        if paragraph.startswith("- ") or paragraph.startswith("* "):
            cleaned = cleaned.lstrip("- *")
            story.append(Paragraph(f"• {cleaned}", styles["BodyText2"]))
        else:
            story.append(Paragraph(cleaned, styles["BodyText2"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#e94560")))
    story.append(Spacer(1, 10))

    # Quiz section
    if questions:
        story.append(Paragraph("Quiz - Test Your Knowledge", styles["SectionHeading"]))
        story.append(Spacer(1, 6))

        for i, q in enumerate(questions, 1):
            story.append(Paragraph(f"Q{i}. {q['question']}", styles["QuizQuestion"]))
            for opt in q.get("options", []):
                story.append(Paragraph(opt, styles["QuizOption"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                f"Answer: {q.get('correct_answer', 'N/A')}",
                styles["QuizAnswer"],
            ))
            explanation = q.get("explanation", "")
            if explanation:
                story.append(Paragraph(
                    f"Explanation: {explanation}",
                    styles["QuizAnswer"],
                ))
            story.append(Spacer(1, 8))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc")))
    story.append(Paragraph(
        "Generated by TubeMentor AI | All Copyrights are reserved to original content creators 2026",
        ParagraphStyle("Footer", parent=styles["BodyText"], fontSize=8,
                        textColor=HexColor("#999999"), alignment=TA_CENTER),
    ))

    doc.build(story)
    return file_name
