"""
Kundli Milan PDF Report — Dharma Path USA Foundation
"""
from __future__ import annotations
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rcanvas

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

PW, PH   = letter
LM, RM   = 50, 50
HDR_H    = 36
FTR_H    = 38
BODY_TOP = PH - HDR_H - 12
BODY_BOT = FTR_H + 12

_QUALITY_COLOR = {
    "good":      colors.HexColor("#15803d"),
    "excellent": colors.HexColor("#15803d"),
    "neutral":   colors.HexColor("#b45309"),
    "bad":       colors.HexColor("#b91c1c"),
}
_RATING_RING = {
    "excellent": colors.HexColor("#15803d"),
    "good":      colors.HexColor("#d97706"),
    "neutral":   colors.HexColor("#b45309"),
    "bad":       colors.HexColor("#b91c1c"),
}


def _header_footer(c, page_num: int):
    c.saveState()
    c.setFillColor(C_MAROON_DARK)
    c.rect(0, PH - HDR_H, PW, HDR_H, fill=1, stroke=0)
    c.setFillColor(C_AMBER)
    c.rect(0, PH - HDR_H, PW, 2, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(LM, PH - 22, "DHARMA PATH USA FOUNDATION")
    c.setFont("Helvetica", 8.5)
    c.drawRightString(PW - RM, PH - 22, f"PAGE {page_num}")
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
    c.restoreState()


def _cover_page(c, data: dict):
    band_h = 210
    c.setFillColor(C_MAROON_DARK)
    c.rect(0, PH - band_h, PW, band_h, fill=1, stroke=0)
    c.setFillColor(C_AMBER)
    c.rect(0, PH - band_h - 3, PW, 3, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(PW / 2, PH - 50, "DHARMA PATH USA FOUNDATION")
    c.setFillColor(C_PEACH)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PW / 2, PH - 68, "Vedic Jyotish  •  Ancient Wisdom  •  Modern Guidance")
    c.setStrokeColor(colors.HexColor("#fbbf24"))
    c.setLineWidth(0.8)
    c.line(LM + 80, PH - 83, PW - RM - 80, PH - 83)
    c.setFillColor(colors.HexColor("#fbbf24"))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PW / 2, PH - 112, "KUNDLI MILAN REPORT")
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica", 10)
    c.drawCentredString(PW / 2, PH - 129, "Ashtakoota Guna Compatibility Analysis")
    c.setFillColor(C_PEACH)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PW / 2, PH - 146, f"Report Date: {datetime.now().strftime('%B %d, %Y')}")
    c.setFillColor(colors.HexColor("#fbbf24"))
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(PW / 2, PH - 163, "Questions? Email: seva@dharmpathusa.com")

    # Cream body
    c.setFillColor(C_CREAM)
    c.rect(0, 0, PW, PH - band_h - 3, fill=1, stroke=0)

    y = PH - band_h - 3 - 22

    boy_name  = data.get("boy",  {}).get("name") or "Boy"
    girl_name = data.get("girl", {}).get("name") or "Girl"
    total     = data["total_score"]
    max_score = data["max_score"]
    pct       = round(total / max_score * 100)
    rc        = data["rating_class"]
    ring_col  = _RATING_RING.get(rc, C_MAROON)

    # Names
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(PW / 2, y, f"{boy_name}  ❤  {girl_name}")
    y -= 26

    # Score circle
    scx, scy = PW / 2, y - 50
    c.setFillColor(ring_col)
    c.circle(scx, scy, 50, fill=1, stroke=0)
    c.setFillColor(C_CREAM)
    c.circle(scx, scy, 43, fill=1, stroke=0)
    c.setFillColor(ring_col)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(scx, scy + 9, str(total))
    c.setFont("Helvetica", 10)
    c.drawCentredString(scx, scy - 7, f"/ {max_score}")
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(scx, scy - 20, f"{pct}%")
    y = scy - 60

    # Rating badge
    badge_w, badge_h = 120, 20
    c.setFillColor(ring_col)
    c.roundRect(PW / 2 - badge_w / 2, y - badge_h, badge_w, badge_h, 7, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(PW / 2, y - 14, data["rating"])
    y -= badge_h + 8

    # Summary
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PW / 2, y, data["summary"])
    y -= 16

    # Score bar
    bar_w = PW - LM - RM - 60
    bar_x = (PW - bar_w) / 2
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(bar_x, y, "Compatibility Score")
    c.drawRightString(bar_x + bar_w, y, f"{total} / {max_score}")
    y -= 10
    c.setFillColor(C_RULE)
    c.roundRect(bar_x, y - 10, bar_w, 10, 3, fill=1, stroke=0)
    c.setFillColor(ring_col)
    c.roundRect(bar_x, y - 10, max(6, bar_w * pct / 100), 10, 3, fill=1, stroke=0)
    y -= 20

    # Moon cards
    boy  = data["boy"]
    girl = data["girl"]
    card_w = (PW - LM - RM - 14) / 2
    card_h = 88

    for i, (person, is_boy) in enumerate([(boy, True), (girl, False)]):
        cx = LM + i * (card_w + 14)
        c.setFillColor(C_WHITE)
        c.roundRect(cx, y - card_h, card_w, card_h, 8, fill=1, stroke=0)
        c.setStrokeColor(C_AMBER)
        c.setLineWidth(1)
        c.roundRect(cx, y - card_h, card_w, card_h, 8, fill=0, stroke=1)
        hdr_col = colors.HexColor("#1d4ed8") if is_boy else colors.HexColor("#c2410c")
        c.setFillColor(hdr_col)
        c.roundRect(cx, y - 22, card_w, 22, 8, fill=1, stroke=0)
        c.rect(cx, y - 22, card_w, 10, fill=1, stroke=0)
        gender = "♂" if is_boy else "♀"
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx + card_w / 2, y - 15,
                            f"{gender} {person.get('name') or ('Boy' if is_boy else 'Girl')}")
        dy2 = y - 36
        rows = [
            ("Nakshatra", f"{person.get('nak_name', '')} Pada {person.get('pada', '')}"),
            ("Rashi",     f"{person.get('rashi', '')} / {person.get('rashi_hindi', '')}"),
        ]
        dob = person.get("dob", "")
        place = person.get("place", "")
        if dob:
            rows.append(("Date", dob))
        if place:
            rows.append(("Place", place[:28]))
        for label, val in rows:
            c.setFillColor(C_GOLD_LBL)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(cx + 10, dy2, f"{label}:")
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica", 7.5)
            c.drawString(cx + 64, dy2, str(val))
            dy2 -= 14

    y -= card_h + 10

    # Note
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(PW / 2, y,
        "This is a detailed Jyotish compatibility report. For a personalised interpretation,")
    c.drawCentredString(PW / 2, y - 12, "please email this report to seva@dharmpathusa.com")
    y -= 28

    # Compact disclaimer box
    disc_lines = [
        "This Kundli Milan report is intended for spiritual guidance and educational purposes only.",
        "It does not constitute professional advice. Dharma Path USA Foundation makes no warranties",
        "regarding accuracy. Consult a qualified Jyotishi for important life decisions.",
        "Free will and the grace of the Divine remain the ultimate determinants of one’s destiny.",
    ]
    line_sp = 13
    box_h = len(disc_lines) * line_sp + 22
    bx = LM + 20
    bw = PW - LM - RM - 40
    c.setFillColor(colors.HexColor("#fff7ed"))
    c.roundRect(bx, y - box_h, bw, box_h, 6, fill=1, stroke=0)
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1)
    c.roundRect(bx, y - box_h, bw, box_h, 6, fill=0, stroke=1)
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(PW / 2, y - 12, "DISCLAIMER")
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica", 7)
    dy3 = y - 24
    for line in disc_lines:
        c.drawCentredString(PW / 2, dy3, line)
        dy3 -= line_sp

    # Bottom brand band
    c.setFillColor(C_MAROON_DARK)
    c.rect(0, 0, PW, 52, fill=1, stroke=0)
    c.setFillColor(C_AMBER)
    c.rect(0, 52, PW, 2, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(PW / 2, 32, "Dharma Path USA Foundation")
    c.setFillColor(C_PEACH)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(PW / 2, 17, "Bringing Ancient Vedic Wisdom to the Modern World")


def _koota_page(c, data: dict):
    _header_footer(c, 2)
    y = BODY_TOP - 8

    # Title
    c.setFillColor(C_MAROON)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LM, y, "Ashtakoota Guna Milan — Detailed Breakdown")
    y -= 8
    c.setStrokeColor(C_AMBER)
    c.setLineWidth(1.5)
    c.line(LM, y, PW - RM, y)
    y -= 14

    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(LM, y, "Eight compatibility factors (Kootas) based on Moon’s Nakshatra at birth.")
    y -= 18

    # Table header
    c.setFillColor(C_SAFFRON)
    c.rect(LM, y - 12 + 4, PW - LM - RM, 16, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(LM + 4,    y - 8, "KOOTA")
    c.drawString(LM + 115,  y - 8, "BOY")
    c.drawString(LM + 290,  y - 8, "SCORE")
    c.drawString(LM + 345,  y - 8, "GIRL")
    c.drawString(LM + 465,  y - 8, "QUALITY")
    y -= 16

    # Koota rows (2 lines each)
    row_h = 28
    for i, k in enumerate(data.get("kootas", [])):
        bg = C_ROW_STRIPE if i % 2 == 0 else C_WHITE
        c.setFillColor(bg)
        c.rect(LM, y - row_h + 4, PW - LM - RM, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_RULE)
        c.setLineWidth(0.3)
        c.line(LM, y - row_h + 4, PW - RM, y - row_h + 4)

        qcol = _QUALITY_COLOR.get(k.get("quality", "neutral"), C_MUTED)
        b_val = str(k.get("p1_value", ""))
        g_val = str(k.get("p2_value", ""))

        # Line 1: name, score, quality badge
        c.setFillColor(C_MAROON)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(LM + 4, y - 8, k["name"])

        c.setFillColor(qcol)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(LM + 290, y - 8, f"{k['score']} / {k['max']}")

        qw, qh = 56, 13
        c.setFillColor(qcol)
        c.roundRect(LM + 465, y - 14, qw, qh, 4, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(LM + 465 + qw / 2, y - 9, k.get("quality", "").upper())

        # Line 2: boy / girl values and detail
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica", 7.5)
        c.drawString(LM + 4,   y - 20, k.get("detail", "")[:48])
        c.setFillColor(C_GOLD_LBL)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(LM + 115, y - 8, b_val[:22])
        c.drawString(LM + 345, y - 8, g_val[:22])

        y -= row_h

    # Total row
    total  = data["total_score"]
    max_s  = data["max_score"]
    c.setFillColor(C_MAROON)
    c.rect(LM, y - 16 + 4, PW - LM - RM, 20, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LM + 4, y - 11, "TOTAL GUNA SCORE")
    c.drawString(LM + 290, y - 11, f"{total} / {max_s}")
    y -= 24

    # Doshas
    doshas = [k for k in data.get("kootas", []) if k.get("dosha")]
    y -= 10
    if doshas:
        c.setFillColor(C_SAFFRON)
        c.rect(LM, y - 12 + 4, PW - LM - RM, 20, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(LM + 8, y - 8, "DOSHA WARNINGS")
        y -= 26

        for k in doshas:
            c.setFillColor(colors.HexColor("#fef2f2"))
            c.roundRect(LM, y - 34, PW - LM - RM, 34, 6, fill=1, stroke=0)
            c.setStrokeColor(colors.HexColor("#b91c1c"))
            c.setLineWidth(0.8)
            c.roundRect(LM, y - 34, PW - LM - RM, 34, 6, fill=0, stroke=1)
            c.setFillColor(colors.HexColor("#b91c1c"))
            c.setFont("Helvetica-Bold", 9)
            c.drawString(LM + 12, y - 13, f"⚠  {k['name']} Dosha")
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica", 8.5)
            c.drawString(LM + 12, y - 25, k.get("detail", ""))
            y -= 44

        c.setFillColor(C_MUTED)
        c.setFont("Helvetica-Oblique", 7.5)
        c.drawString(LM, y, "Consult a qualified Jyotishi for Dosha remedies and guidance.")
    else:
        c.setFillColor(colors.HexColor("#f0fdf4"))
        c.roundRect(LM, y - 26, PW - LM - RM, 26, 6, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#15803d"))
        c.setLineWidth(0.8)
        c.roundRect(LM, y - 26, PW - LM - RM, 26, 6, fill=0, stroke=1)
        c.setFillColor(colors.HexColor("#15803d"))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(PW / 2, y - 16,
            "✓  No major Doshas — Nadi, Bhakoot and Gana are all compatible.")


def build_milan_pdf(data: dict, path: str) -> str:
    c = rcanvas.Canvas(path, pagesize=letter)
    c.setTitle("Kundli Milan Report — Dharma Path USA Foundation")
    c.setAuthor("Dharma Path USA Foundation")
    c.setSubject("Vedic Astrology Compatibility Report")

    _cover_page(c, data)
    c.showPage()

    _koota_page(c, data)

    c.save()
    return path
