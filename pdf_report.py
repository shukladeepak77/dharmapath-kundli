"""
Professional PDF Kundli Report — Dharma Path USA Foundation
"""
from __future__ import annotations
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pdf_chart import draw_north_indian_chart

# ── Optional Devanagari font for OM symbol ────────────────────────────────────
_DEVA_FONT = None
for _fp in [
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
    "/usr/share/fonts/truetype/fonts-deva-extra/chandas.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
]:
    if os.path.exists(_fp):
        try:
            pdfmetrics.registerFont(TTFont("DevaFont", _fp))
            _DEVA_FONT = "DevaFont"
        except Exception:
            pass
        break

# ── Brand palette ─────────────────────────────────────────────────────────────
C_MAROON_DARK = colors.HexColor("#3b0a00")
C_MAROON      = colors.HexColor("#7c2d12")
C_SAFFRON     = colors.HexColor("#c2410c")
C_AMBER       = colors.HexColor("#d97706")
C_GOLD_LBL    = colors.HexColor("#92400e")
C_CREAM       = colors.HexColor("#fffbeb")
C_ROW_STRIPE  = colors.HexColor("#fef3c7")
C_RULE        = colors.HexColor("#d6d3d1")
C_TEXT        = colors.HexColor("#1c1917")
C_MUTED       = colors.HexColor("#78716c")
C_WHITE       = colors.white
C_PEACH       = colors.HexColor("#fed7aa")

# ── Page geometry ─────────────────────────────────────────────────────────────
PW, PH   = letter            # 612 × 792 pt
LM, RM   = 50, 50
HDR_H    = 36                # running header band height
FTR_H    = 38                # footer band height
BODY_TOP = PH - HDR_H - 12  # first content y
BODY_BOT = FTR_H + 12       # last content y

PLANET_ORDER = [
    "Lagna", "Sun", "Moon", "Mars", "Mercury",
    "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
]

DASHA_COLORS = {
    "Sun":     colors.HexColor("#dc2626"),
    "Moon":    colors.HexColor("#2563eb"),
    "Mars":    colors.HexColor("#b91c1c"),
    "Mercury": colors.HexColor("#059669"),
    "Jupiter": colors.HexColor("#d97706"),
    "Venus":   colors.HexColor("#7c3aed"),
    "Saturn":  colors.HexColor("#374151"),
    "Rahu":    colors.HexColor("#0891b2"),
    "Ketu":    colors.HexColor("#78350f"),
}


# ── Running header / footer ───────────────────────────────────────────────────

def _header_footer(c, section: str, page_num: int):
    c.saveState()

    # Header band
    c.setFillColor(C_MAROON_DARK)
    c.rect(0, PH - HDR_H, PW, HDR_H, fill=1, stroke=0)
    # Amber accent line
    c.setFillColor(C_AMBER)
    c.rect(0, PH - HDR_H, PW, 2, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(LM, PH - 22, "DHARMA PATH USA FOUNDATION")
    c.setFont("Helvetica", 8.5)
    c.drawRightString(PW - RM, PH - 22, f"PAGE {page_num}")

    # Footer line
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1)
    c.line(LM, FTR_H, PW - RM, FTR_H)
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(
        LM, FTR_H - 14,
        f"Dharma Path USA Foundation  |  "
        f"Generated: {datetime.now().strftime('%B %d, %Y')}  |  "
        "For spiritual guidance & educational purposes only",
    )
    c.setFont("Helvetica", 7)
    c.drawRightString(PW - RM, FTR_H - 14, f"Page {page_num}")

    c.restoreState()


def _new_content_page(c, section: str, page_num: int) -> float:
    _header_footer(c, section, page_num)
    return BODY_TOP


# ── Shared drawing helpers ────────────────────────────────────────────────────

def _section_bar(c, y: float, text: str) -> float:
    """Dark maroon full-width bar with white label. Returns y below."""
    c.saveState()
    c.setFillColor(C_MAROON)
    c.rect(LM, y - 16, PW - LM - RM, 20, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(LM + 8, y - 10, text.upper())
    c.restoreState()
    return y - 26


def _table_header(c, y: float, cols: list[tuple[str, float]]) -> float:
    """Saffron column-header row. Returns y below."""
    h = 16
    c.saveState()
    c.setFillColor(C_SAFFRON)
    c.rect(LM, y - h + 4, PW - LM - RM, h, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 8)
    for label, xp in cols:
        c.drawString(xp, y - 10, label)
    c.restoreState()
    return y - h


def _planet_table(c, y: float, chart: dict) -> float:
    """Striped planetary positions table. Returns y below last row."""
    cols: list[tuple[str, float]] = [
        ("PLANET",    LM + 4),
        ("RASHI",     LM + 80),
        ("DEG°", LM + 178),
        ("HOUSE",     LM + 230),
        ("NAKSHATRA", LM + 282),
        ("PADA",      LM + 400),
        ("℞",    LM + 440),
    ]
    y = _table_header(c, y, cols)
    row_h = 14

    for i, planet in enumerate(PLANET_ORDER):
        pos = chart[planet]
        bg = C_ROW_STRIPE if i % 2 == 0 else C_WHITE
        c.saveState()
        c.setFillColor(bg)
        c.rect(LM, y - 2, PW - LM - RM, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.3)
        c.line(LM, y - 2, PW - RM, y - 2)

        is_lagna = planet == "Lagna"
        c.setFillColor(C_MAROON if is_lagna else C_TEXT)
        c.setFont("Helvetica-Bold" if is_lagna else "Helvetica", 8.5)
        c.drawString(LM + 4, y + 2, planet)

        c.setFillColor(C_TEXT)
        c.setFont("Helvetica", 8.5)
        c.drawString(LM + 80,  y + 2, pos["rashi"])
        c.drawString(LM + 178, y + 2, f"{pos['degree_in_rashi']:.2f}°")
        c.drawString(LM + 230, y + 2, str(pos["house"]))
        c.drawString(LM + 282, y + 2, pos["nakshatra"])
        c.drawString(LM + 400, y + 2, str(pos["pada"]))

        if pos.get("retrograde") and planet not in ("Lagna", "Rahu", "Ketu"):
            c.setFillColor(C_SAFFRON)
            c.setFont("Helvetica-Bold", 8.5)
            c.drawString(LM + 440, y + 2, "℞")

        c.restoreState()
        y -= row_h

    c.saveState()
    c.setStrokeColor(C_MAROON)
    c.setLineWidth(0.6)
    c.line(LM, y, PW - RM, y)
    c.restoreState()
    return y - 8


# ── Cover page ────────────────────────────────────────────────────────────────

def _cover_page(c, bd: dict, result: dict):
    # ── Dark top band ─────────────────────────────────────────────────────────
    band_h = 265
    c.setFillColor(C_MAROON_DARK)
    c.rect(0, PH - band_h, PW, band_h, fill=1, stroke=0)
    # Amber accent stripe at bottom of band
    c.setFillColor(C_AMBER)
    c.rect(0, PH - band_h - 3, PW, 3, fill=1, stroke=0)

    # OM symbol (only when Devanagari font is available)
    if _DEVA_FONT:
        c.setFillColor(colors.HexColor("#fbbf24"))
        c.setFont(_DEVA_FONT, 52)
        c.drawCentredString(PW / 2, PH - 70, "ॐ")

    # Foundation name
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(PW / 2, PH - 108, "DHARMA PATH USA FOUNDATION")

    # Tagline
    c.setFillColor(C_PEACH)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(
        PW / 2, PH - 127,
        "Vedic Jyotish  •  Ancient Wisdom  •  Modern Guidance",
    )

    # Thin gold divider
    c.setStrokeColor(colors.HexColor("#fbbf24"))
    c.setLineWidth(0.8)
    c.line(LM + 60, PH - 142, PW - RM - 60, PH - 142)

    # Report title
    c.setFillColor(colors.HexColor("#fbbf24"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PW / 2, PH - 172, "JANAM KUNDLI")

    c.setFillColor(C_WHITE)
    c.setFont("Helvetica", 11)
    c.drawCentredString(PW / 2, PH - 192, "Vedic Birth Chart & Astrological Report")

    c.setStrokeColor(C_PEACH)
    c.setLineWidth(0.5)
    c.line(LM + 100, PH - 207, PW - RM - 100, PH - 207)

    c.setFillColor(C_PEACH)
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        PW / 2, PH - 222,
        f"Report Date: {datetime.now().strftime('%B %d, %Y')}",
    )

    c.setFillColor(colors.HexColor("#fbbf24"))
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(
        PW / 2, PH - 242,
        "Questions? Email us at  seva@dharmpathusa.com",
    )

    # ── Cream body ────────────────────────────────────────────────────────────
    c.setFillColor(C_CREAM)
    c.rect(0, 0, PW, PH - band_h - 3, fill=1, stroke=0)

    # ── Native info box ───────────────────────────────────────────────────────
    bx = LM + 28
    bw = PW - 2 * (LM + 28)
    bh = 200
    by = PH - band_h - 3 - 28 - bh   # bottom of box

    # Note just above birth details box
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(
        PW / 2, by + bh + 19,
        "This is a detailed Jyotish report. For a personalised interpretation summary,",
    )
    c.drawCentredString(
        PW / 2, by + bh + 7,
        "please email this report to seva@dharmpathusa.com",
    )

    # Shadow
    c.setFillColor(C_RULE)
    c.roundRect(bx + 3, by - 3, bw, bh, 10, fill=1, stroke=0)

    # White fill
    c.setFillColor(C_WHITE)
    c.roundRect(bx, by, bw, bh, 10, fill=1, stroke=0)

    # Maroon header stripe inside box (top-rounded, bottom-flat)
    c.setFillColor(C_MAROON)
    c.roundRect(bx, by + bh - 32, bw, 32, 10, fill=1, stroke=0)
    c.rect(bx, by + bh - 32, bw, 14, fill=1, stroke=0)   # flatten bottom corners

    # Amber border on top of everything
    c.setFillColor(colors.transparent)
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1.5)
    c.roundRect(bx, by, bw, bh, 10, fill=0, stroke=1)

    # Header label in stripe
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(bx + bw / 2, by + bh - 21, "Birth Details")

    # Detail rows
    birth_dt   = bd.get("birth_datetime_local", "")
    birth_date = birth_dt.split(" ")[0] if " " in birth_dt else birth_dt
    birth_time = birth_dt.split(" ")[1][:5] if " " in birth_dt else "—"

    details = [
        ("Date of Birth",    birth_date),
        ("Time of Birth",    birth_time),
        ("Birth Place",      bd.get("place", "—")),
        ("Coordinates",      f"Lat {bd.get('latitude', '—')}°  ·  Lon {bd.get('longitude', '—')}°"),
        ("Timezone",         f"UTC {bd.get('timezone_offset_hours', 0):+}"),
        ("Ayanamsha",         f"{result.get('ayanamsha_lahiri', '—')}°"),
    ]

    dy = by + bh - 52
    for label, value in details:
        c.setFillColor(C_GOLD_LBL)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(bx + 18, dy, label + ":")
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica", 8.5)
        c.drawString(bx + 148, dy, str(value))
        dy -= 17

    # ── Shloka & disclaimer ───────────────────────────────────────────────────
    shloka_y = by - 22
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-BoldOblique", 8.5)
    c.drawCentredString(
        PW / 2, shloka_y,
        "“Yatha Pinde Tatha Brahmande”  —  "
        "As in the microcosm, so in the macrocosm",
    )

    c.setStrokeColor(C_AMBER)
    c.setLineWidth(0.8)
    c.line(LM + 60, shloka_y - 12, PW - RM - 60, shloka_y - 12)

    disclaimer_lines = [
        "This Janam Kundli report is intended solely for spiritual guidance, self-reflection,",
        "and educational purposes. It does not constitute medical, psychological, legal,",
        "financial, or any other form of professional advice. Astrological interpretations are",
        "rooted in classical Vedic Jyotish traditions and are presented as one lens through",
        "which to understand life patterns — not as deterministic predictions or guaranteed",
        "outcomes. Individual results may vary. Dharma Path USA Foundation makes no warranties,",
        "express or implied, regarding the accuracy, completeness, or suitability of this report",
        "for any particular purpose. The Foundation assumes no liability for any decisions,",
        "actions, or consequences arising from use of this report. Free will, sincere personal",
        "effort, and the grace of the Divine remain the ultimate determinants of one’s destiny.",
    ]
    line_spacing = 14
    box_padding = 10
    box_h = len(disclaimer_lines) * line_spacing + box_padding * 2 + 4
    box_y = shloka_y - 22 - box_h
    box_x = LM + 20
    box_w = PW - LM - RM - 40

    # Light background box with amber border
    c.setFillColor(colors.HexColor("#fffbeb"))
    c.roundRect(box_x, box_y, box_w, box_h, 6, fill=1, stroke=0)
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1)
    c.roundRect(box_x, box_y, box_w, box_h, 6, fill=0, stroke=1)

    # "DISCLAIMER" label
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(PW / 2, box_y + box_h - box_padding - 2, "DISCLAIMER")

    c.setFillColor(C_TEXT)
    c.setFont("Helvetica", 8)
    dy = box_y + box_h - box_padding - 16
    for line in disclaimer_lines:
        c.drawCentredString(PW / 2, dy, line)
        dy -= line_spacing

    # ── Bottom brand band ─────────────────────────────────────────────────────
    c.setFillColor(C_MAROON_DARK)
    c.rect(0, 0, PW, 52, fill=1, stroke=0)
    c.setFillColor(C_AMBER)
    c.rect(0, 52, PW, 2, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(PW / 2, 32, "Dharma Path USA Foundation")
    c.setFillColor(C_PEACH)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(
        PW / 2, 17,
        "Bringing Ancient Vedic Wisdom to the Modern World",
    )


# ── Chart + table page ────────────────────────────────────────────────────────

def _chart_and_table_page(
    c,
    page_num: int,
    chart_visual: dict,
    chart_data: dict,
    chart_label: str,
    section_name: str,
):
    y = _new_content_page(c, section_name, page_num)
    y -= 8

    # Centered chart
    chart_size = 310
    cx = (PW - chart_size) / 2
    cy = y - chart_size - 16   # bottom-left of chart

    draw_north_indian_chart(c, chart_visual, cx, cy, chart_size, chart_label)

    y = cy - 18

    # Intro note
    c.saveState()
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Oblique", 7.5)
    note = (
        "D1 Rashi Chart shows natal planetary positions used for all core life interpretations."
        if "D1" in chart_label
        else "D9 Navamsa Chart reveals inner planetary strength, marriage themes and dharmic depth."
    )
    c.drawCentredString(PW / 2, y, note)
    c.restoreState()
    y -= 14

    y = _section_bar(c, y, f"{chart_label} — Planetary Positions")
    _planet_table(c, y, chart_data)


# ── Mahadasha page ────────────────────────────────────────────────────────────

def _dasha_page(c, page_num: int, result: dict):
    y = _new_content_page(c, "Vimshottari Mahadasha", page_num)
    y -= 8

    # Page title
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(LM, y, "Vimshottari Mahadasha")
    y -= 8
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1.5)
    c.line(LM, y, PW - RM, y)
    y -= 14

    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawString(
        LM, y,
        "Planetary periods calculated from Moon’s Nakshatra at birth "
        "(120-year Vimshottari cycle).",
    )
    y -= 22

    # Table header
    cols: list[tuple[str, float]] = [
        ("MAHADASHA LORD", LM + 22),
        ("START DATE",     LM + 175),
        ("END DATE",       LM + 295),
        ("DURATION",       LM + 410),
    ]
    y = _table_header(c, y, cols)

    dashas = result.get("vimshottari_mahadasha", [])
    d1 = result.get("d1_rashi_chart", {})
    row_h = 26

    for i, d in enumerate(dashas):
        bg = C_ROW_STRIPE if i % 2 == 0 else C_WHITE
        lord = d["lord"]
        dot_col = DASHA_COLORS.get(lord, C_TEXT)

        c.saveState()
        c.setFillColor(bg)
        c.rect(LM, y - row_h + 4, PW - LM - RM, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.3)
        c.line(LM, y - row_h + 4, PW - RM, y - row_h + 4)

        # Color dot
        c.setFillColor(dot_col)
        c.circle(LM + 10, y - 5, 5, fill=1, stroke=0)

        # Lord name
        c.setFillColor(dot_col)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(LM + 22, y - 2, lord)

        # Planet placement info below lord name
        pos = d1.get(lord, {})
        if pos:
            c.setFillColor(C_MUTED)
            c.setFont("Helvetica", 7.5)
            c.drawString(
                LM + 22, y - 14,
                f"{pos.get('rashi','')} · House {pos.get('house','')} · {pos.get('nakshatra','')}",
            )

        c.setFillColor(C_TEXT)
        c.setFont("Helvetica", 9.5)
        c.drawString(LM + 175, y - 5, d["start"])
        c.drawString(LM + 295, y - 5, d["end"])
        c.drawString(LM + 410, y - 5, f"{d['years']} yrs")
        c.restoreState()
        y -= row_h

    c.saveState()
    c.setStrokeColor(C_MAROON)
    c.setLineWidth(0.8)
    c.line(LM, y, PW - RM, y)
    c.restoreState()
    y -= 18

    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(
        LM, y,
        "✱  Sub-period (Antardasha) and Pratyantardasha calculations available on request.",
    )
    y -= 40

    # Next-page notice box
    box_w = PW - LM - RM
    box_h = 52
    c.setFillColor(colors.HexColor("#fff7ed"))
    c.roundRect(LM, y - box_h, box_w, box_h, 8, fill=1, stroke=0)
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1.2)
    c.roundRect(LM, y - box_h, box_w, box_h, 8, fill=0, stroke=1)

    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PW / 2, y - 20, "Kundli Insights & Reflections")
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PW / 2, y - 36, "The Vedic analysis and planetary insights begin on the next page.")


# ── Interpretation pages ──────────────────────────────────────────────────────

def _interpretation_pages(c, start_page: int, sections: list):
    page_num = start_page
    y = _new_content_page(c, "Kundli Interpretation", page_num)
    y -= 8

    y -= 8

    usable_w = PW - LM - RM - 16   # indent for accent bar

    for section in sections:
        # Ensure room for header + at least one line
        if y < BODY_BOT + 55:
            c.showPage()
            page_num += 1
            y = _new_content_page(c, "Kundli Interpretation", page_num)
            y -= 8

        # Left accent bar + section title
        c.saveState()
        c.setFillColor(C_SAFFRON)
        c.rect(LM, y - 14, 4, 20, fill=1, stroke=0)
        c.setFillColor(C_MAROON)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(LM + 12, y - 8, section["title"])
        c.restoreState()
        y -= 22

        for para in section["paragraphs"]:
            words = para.split()
            line = ""
            for word in words:
                test = (line + " " + word).strip()
                if c.stringWidth(test, "Helvetica", 9) <= usable_w:
                    line = test
                else:
                    if line:
                        if y < BODY_BOT:
                            c.showPage()
                            page_num += 1
                            y = _new_content_page(c, "Kundli Interpretation", page_num)
                            y -= 8
                        c.setFillColor(C_TEXT)
                        c.setFont("Helvetica", 9)
                        c.drawString(LM + 12, y, line)
                        y -= 13
                    line = word

            if line:
                if y < BODY_BOT:
                    c.showPage()
                    page_num += 1
                    y = _new_content_page(c, "Kundli Interpretation", page_num)
                    y -= 8
                c.setFillColor(C_TEXT)
                c.setFont("Helvetica", 9)
                c.drawString(LM + 12, y, line)
                y -= 13
            y -= 5

        y -= 8
        # Thin separator between sections
        if y > BODY_BOT + 16:
            c.saveState()
            c.setStrokeColor(C_RULE)
            c.setLineWidth(0.4)
            c.line(LM + 12, y, PW - RM, y)
            c.restoreState()
            y -= 10


# ── Main entry point ──────────────────────────────────────────────────────────

def build_kundli_pdf(result: dict, interpretation_sections: list, path: str) -> str:
    c = rcanvas.Canvas(path, pagesize=letter)
    c.setTitle("Janam Kundli — Dharma Path USA Foundation")
    c.setAuthor("Dharma Path USA Foundation")
    c.setSubject("Vedic Astrology Birth Chart Report")
    c.setCreator("DharmaPath Jyotish Engine")

    bd = result["birth_data"]

    # Page 1: Cover (no running header/footer)
    _cover_page(c, bd, result)
    c.showPage()

    # Page 2: D1 Rashi Chart
    _chart_and_table_page(
        c, 2,
        result["d1_chart_visual"],
        result["d1_rashi_chart"],
        "D1 Rashi Chart",
        "D1 Rashi Chart",
    )
    c.showPage()

    # Page 3: D9 Navamsa Chart
    _chart_and_table_page(
        c, 3,
        result["d9_chart_visual"],
        result["d9_navamsa_chart"],
        "D9 Navamsa Chart",
        "D9 Navamsa Chart",
    )
    c.showPage()

    # Page 4: Vimshottari Mahadasha
    _dasha_page(c, 4, result)
    c.showPage()

    # Page 5+: Interpretation
    _interpretation_pages(c, 5, interpretation_sections)

    c.save()
    return path
