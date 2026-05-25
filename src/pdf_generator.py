"""
Generates the weekly PDF memo and daily flash PDF using ReportLab.
Clean, professional layout optimised for on-screen reading and printing.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── WWT brand colours ─────────────────────────────────────────────────────────
WWT_DARK  = colors.HexColor("#002855")   # WWT dark navy
WWT_BLUE  = colors.HexColor("#005eb8")   # WWT primary blue
WWT_LIGHT = colors.HexColor("#e8f0fa")   # light blue tint for backgrounds
GREY_MID  = colors.HexColor("#6b7280")
GREY_LIGHT = colors.HexColor("#f3f4f6")

# Status badge colours
STATUS_COLORS = {
    "ENACTED":        colors.HexColor("#dc2626"),  # red — in force now
    "PASSED-PENDING": colors.HexColor("#ea580c"),  # orange — passed, not yet live
    "PROPOSED":       colors.HexColor("#ca8a04"),  # amber — formal proposal
    "CONSULTATION":   colors.HexColor("#2563eb"),  # blue — open for comment
    "RUMORED":        colors.HexColor("#6b7280"),  # grey — unconfirmed
}

SIGNIFICANCE_COLORS = {
    "HIGH":   colors.HexColor("#dc2626"),
    "MEDIUM": colors.HexColor("#ea580c"),
    "LOW":    colors.HexColor("#16a34a"),
}

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm


def _build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", parent=base["Title"],
        fontSize=26, leading=32, textColor=WWT_DARK,
        spaceAfter=6, alignment=TA_LEFT,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", parent=base["Normal"],
        fontSize=13, leading=18, textColor=WWT_BLUE,
        spaceAfter=4, alignment=TA_LEFT,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta", parent=base["Normal"],
        fontSize=10, leading=14, textColor=GREY_MID,
        alignment=TA_LEFT,
    )
    styles["section_head"] = ParagraphStyle(
        "section_head", parent=base["Heading1"],
        fontSize=14, leading=18, textColor=WWT_DARK,
        spaceBefore=14, spaceAfter=6, borderPad=0,
    )
    styles["item_title"] = ParagraphStyle(
        "item_title", parent=base["Normal"],
        fontSize=11, leading=15, textColor=WWT_DARK,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3,
    )
    styles["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=10, leading=14, textColor=colors.HexColor("#1f2937"),
        alignment=TA_JUSTIFY, spaceAfter=4,
    )
    styles["label"] = ParagraphStyle(
        "label", parent=base["Normal"],
        fontSize=9, leading=12, textColor=GREY_MID,
        fontName="Helvetica-Bold", spaceAfter=2,
    )
    styles["footnote"] = ParagraphStyle(
        "footnote", parent=base["Normal"],
        fontSize=8, leading=11, textColor=GREY_MID, spaceAfter=2,
    )
    styles["exec_body"] = ParagraphStyle(
        "exec_body", parent=base["Normal"],
        fontSize=10.5, leading=16, textColor=colors.HexColor("#1f2937"),
        alignment=TA_JUSTIFY, spaceAfter=8,
    )
    styles["flash_title"] = ParagraphStyle(
        "flash_title", parent=base["Normal"],
        fontSize=13, leading=17, textColor=colors.HexColor("#dc2626"),
        fontName="Helvetica-Bold", spaceAfter=6,
    )
    return styles


def _status_badge(status: str, styles) -> Paragraph:
    colour = STATUS_COLORS.get(status, GREY_MID)
    hex_c  = colour.hexval() if hasattr(colour, "hexval") else "#6b7280"
    return Paragraph(
        f'<font color="{hex_c}"><b>● {status}</b></font>',
        styles["label"],
    )


def _significance_chip(sig: str, styles) -> Paragraph:
    colour = SIGNIFICANCE_COLORS.get(sig, GREY_MID)
    hex_c  = colour.hexval() if hasattr(colour, "hexval") else "#6b7280"
    return Paragraph(
        f'<font color="{hex_c}"><b>{sig} SIGNIFICANCE</b></font>',
        styles["label"],
    )


def _hr():
    return HRFlowable(width="100%", thickness=0.5, color=GREY_LIGHT, spaceAfter=4)


def _category_label(categories: list[str]) -> str:
    return " · ".join(c.replace("_", " ").title() for c in (categories or [])[:4])


def _vertical_label(verticals: list[str]) -> str:
    return " · ".join(v.replace("_", " ").title() for v in (verticals or [])[:4])


def _render_item(item: dict, footnote_start: int, styles) -> tuple[list, list, int]:
    """Render a single regulatory item. Returns (flowables, footnote_entries, next_fn_idx)."""
    flowables = []
    footnotes = []
    fn_idx = footnote_start

    # Item title
    flowables.append(Paragraph(item.get("title", "Untitled"), styles["item_title"]))

    # Status + significance row
    status = item.get("status", "UNKNOWN")
    sig    = item.get("significance", "LOW")
    meta_text = (
        f'<b>{item.get("jurisdiction","")}</b> &nbsp;|&nbsp; '
        f'<font color="{STATUS_COLORS.get(status, GREY_MID).hexval()}">'
        f'<b>{status}</b></font>'
        f'&nbsp;|&nbsp; '
        f'<font color="{SIGNIFICANCE_COLORS.get(sig, GREY_MID).hexval()}">'
        f'<b>{sig}</b></font>'
    )
    if item.get("status_note"):
        meta_text += f' &nbsp;— {item["status_note"]}'
    flowables.append(Paragraph(meta_text, styles["label"]))
    flowables.append(Spacer(1, 3))

    # IT categories + verticals
    cats  = _category_label(item.get("it_categories", []))
    verts = _vertical_label(item.get("verticals", []))
    if cats:
        flowables.append(Paragraph(f"IT: {cats}", styles["footnote"]))
    if verts:
        flowables.append(Paragraph(f"Sectors: {verts}", styles["footnote"]))
    flowables.append(Spacer(1, 4))

    # Summary
    flowables.append(Paragraph("<b>Summary</b>", styles["label"]))
    flowables.append(Paragraph(item.get("summary", ""), styles["body"]))

    # WWT relevance
    flowables.append(Paragraph("<b>WWT Relevance</b>", styles["label"]))
    flowables.append(Paragraph(item.get("wwt_relevance", ""), styles["body"]))

    # Sources as footnotes
    sources = item.get("sources", [])
    if sources:
        src_labels = []
        for src in sources:
            src_title = src.get("title", "Source")
            src_url   = src.get("url", "")
            src_labels.append(f"[{fn_idx}]")
            footnotes.append(
                Paragraph(
                    f'[{fn_idx}] <a href="{src_url}" color="blue">'
                    f'{src_title}</a> — {src_url}',
                    styles["footnote"],
                )
            )
            fn_idx += 1
        flowables.append(
            Paragraph("Sources: " + " ".join(src_labels), styles["footnote"])
        )

    flowables.append(_hr())
    return flowables, footnotes, fn_idx


def generate_weekly_pdf(
    items: list[dict],
    executive_summary: str,
    run_date: datetime,
) -> bytes:
    """Generate the full weekly memo as a PDF and return raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"APAC Regulatory Intelligence Memo — {run_date.strftime('%d %b %Y')}",
        author="WWT APAC Regulatory Monitor",
    )
    styles = _build_styles()
    story  = []
    all_footnotes: list = []
    fn_idx = 1

    # ── Cover section ────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("APAC Regulatory Intelligence Monitor", styles["cover_title"]))
    story.append(Paragraph(
        f"Week of {run_date.strftime('%d %B %Y')}",
        styles["cover_sub"],
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "World Wide Technology &nbsp;·&nbsp; Confidential — Internal Use Only",
        styles["cover_meta"],
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=WWT_BLUE, spaceAfter=12))
    story.append(Spacer(1, 0.5 * cm))

    # ── Summary stats table ──────────────────────────────────────────────────
    high   = sum(1 for i in items if i.get("significance") == "HIGH")
    medium = sum(1 for i in items if i.get("significance") == "MEDIUM")
    low    = sum(1 for i in items if i.get("significance") == "LOW")
    juris  = sorted({i.get("jurisdiction","") for i in items if i.get("jurisdiction")})

    stat_data = [
        [
            Paragraph(f"<b>{len(items)}</b><br/>Total Items", styles["body"]),
            Paragraph(f'<font color="#dc2626"><b>{high}</b></font><br/>High', styles["body"]),
            Paragraph(f'<font color="#ea580c"><b>{medium}</b></font><br/>Medium', styles["body"]),
            Paragraph(f'<font color="#16a34a"><b>{low}</b></font><br/>Low', styles["body"]),
            Paragraph(f"<b>{len(juris)}</b><br/>Jurisdictions", styles["body"]),
        ]
    ]
    stat_table = Table(
        stat_data,
        colWidths=[(PAGE_W - 2 * MARGIN) / 5] * 5,
        hAlign="LEFT",
    )
    stat_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), WWT_LIGHT),
        ("BOX",         (0, 0), (-1, -1), 0.5, WWT_BLUE),
        ("INNERGRID",   (0, 0), (-1, -1), 0.3, WWT_BLUE),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Executive Summary ────────────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", styles["section_head"]))
    story.append(_hr())
    for para in executive_summary.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), styles["exec_body"]))

    story.append(PageBreak())

    # ── Detailed Findings ────────────────────────────────────────────────────
    story.append(Paragraph("Detailed Findings", styles["section_head"]))
    story.append(Paragraph(
        "Items are ordered by significance (High → Medium → Low) then by jurisdiction.",
        styles["footnote"],
    ))
    story.append(_hr())

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    sorted_items = sorted(items, key=lambda i: (order.get(i.get("significance","LOW"), 2), i.get("jurisdiction","")))

    for item in sorted_items:
        flowables, footnotes, fn_idx = _render_item(item, fn_idx, styles)
        story.extend(flowables)
        all_footnotes.extend(footnotes)

    # ── Source Index ─────────────────────────────────────────────────────────
    if all_footnotes:
        story.append(PageBreak())
        story.append(Paragraph("Source Index", styles["section_head"]))
        story.append(_hr())
        story.extend(all_footnotes)

    doc.build(story)
    return buf.getvalue()


def generate_flash_pdf(
    items: list[dict],
    flash_summary: str,
    run_date: datetime,
) -> bytes:
    """Generate the daily flash digest as a compact PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"APAC Reg Flash — {run_date.strftime('%d %b %Y')}",
    )
    styles  = _build_styles()
    story   = []
    all_footnotes: list = []
    fn_idx = 1

    story.append(Paragraph(
        f"⚡ APAC REGULATORY FLASH — {run_date.strftime('%d %B %Y').upper()}",
        styles["flash_title"],
    ))
    story.append(Paragraph(
        "World Wide Technology &nbsp;·&nbsp; Confidential — Internal Use Only",
        styles["cover_meta"],
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#dc2626"), spaceAfter=10))

    for para in flash_summary.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), styles["exec_body"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("HIGH-Significance Items Detected Today", styles["section_head"]))
    story.append(_hr())

    for item in items:
        flowables, footnotes, fn_idx = _render_item(item, fn_idx, styles)
        story.extend(flowables)
        all_footnotes.extend(footnotes)

    if all_footnotes:
        story.append(Paragraph("Sources", styles["section_head"]))
        story.append(_hr())
        story.extend(all_footnotes)

    doc.build(story)
    return buf.getvalue()
