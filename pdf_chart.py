from reportlab.lib import colors

# ── House cell centres (as fractions of chart size) ──────────────────────────
# North Indian style: house 1 is top-centre diamond
HOUSE_POSITIONS = {
    1:  (0.50, 0.18),
    2:  (0.28, 0.14),
    3:  (0.14, 0.28),
    4:  (0.18, 0.50),
    5:  (0.14, 0.72),
    6:  (0.28, 0.86),
    7:  (0.50, 0.82),
    8:  (0.72, 0.86),
    9:  (0.86, 0.72),
    10: (0.82, 0.50),
    11: (0.86, 0.28),
    12: (0.72, 0.14),
}

# Bilingual planet labels
PLANET_FULL_NAMES = {
    "La":  "Lagna",
    "Su":  "Sun / Surya",
    "Mo":  "Moon / Chandra",
    "Ma":  "Mars / Mangal",
    "Me":  "Mercury / Budh",
    "Ju":  "Jupiter / Guru",
    "Ve":  "Venus / Shukra",
    "Sa":  "Saturn / Shani",
    "Ra":  "Rahu",
    "Ke":  "Ketu",
}

# Planet text colors
PLANET_COLORS = {
    "Su":  colors.HexColor("#dc2626"),   # red — Sun
    "Mo":  colors.HexColor("#2563eb"),   # blue — Moon
    "Ma":  colors.HexColor("#b91c1c"),   # dark red — Mars
    "Me":  colors.HexColor("#059669"),   # green — Mercury
    "Ju":  colors.HexColor("#d97706"),   # amber — Jupiter
    "Ve":  colors.HexColor("#7c3aed"),   # violet — Venus
    "Sa":  colors.HexColor("#374151"),   # dark gray — Saturn
    "Ra":  colors.HexColor("#0891b2"),   # teal — Rahu
    "Ke":  colors.HexColor("#78350f"),   # brown — Ketu
    "La":  colors.HexColor("#7c2d12"),   # maroon — Lagna
}

# House type highlights
_KENDRA    = {1, 4, 7, 10}
_TRIKONA   = {1, 5, 9}
_UPACHAYA  = {3, 6, 10, 11}
_DUSTHANA  = {6, 8, 12}

_COL_LAGNA   = colors.HexColor("#fff7ed")   # warm orange tint for house 1
_COL_KENDRA  = colors.HexColor("#f0fdf4")   # light green tint
_COL_TRIKONA = colors.HexColor("#fffbeb")   # light amber tint
_COL_NEUTRAL = colors.HexColor("#fafafa")   # near-white


def _house_bg_color(house_num: int, is_lagna: bool):
    if is_lagna:
        return _COL_LAGNA
    if house_num in _KENDRA:
        return _COL_KENDRA
    if house_num in _TRIKONA:
        return _COL_TRIKONA
    return _COL_NEUTRAL


def draw_north_indian_chart(c, chart_visual, x, y, size, title="D1 Rashi Chart"):
    """
    Draw a professional North Indian kundli chart into a ReportLab canvas.

    Parameters
    ----------
    c      : ReportLab canvas
    x, y   : bottom-left corner of the chart square
    size   : width = height of the chart square
    title  : label drawn above the chart
    """
    c.saveState()

    lagna_house = 1   # house 1 is always Lagna in North Indian style

    # ── Outer background ──────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#fffaf0"))
    c.rect(x, y, size, size, fill=1, stroke=0)

    # ── Structure lines ───────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#7c2d12"))
    c.setLineWidth(2)

    # Outer square
    c.rect(x, y, size, size, fill=0, stroke=1)

    # Main diagonals
    c.line(x,          y + size, x + size, y)
    c.line(x,          y,        x + size, y + size)

    # Inner diamond lines
    mid = size / 2
    c.line(x + mid,    y + size, x + size, y + mid)
    c.line(x + size,   y + mid,  x + mid,  y)
    c.line(x + mid,    y,        x,         y + mid)
    c.line(x,          y + mid,  x + mid,   y + size)

    # ── Chart title ───────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#7c2d12"))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + mid, y + size + 14, title)

    # ── House cells ───────────────────────────────────────────────────────────
    houses = chart_visual["houses"]

    for house_num in range(1, 13):
        house    = houses[str(house_num)]
        px, py   = HOUSE_POSITIONS[house_num]
        is_lagna = (house_num == lagna_house)

        tx = x + px * size
        ty = y + (1 - py) * size

        # Nudge labels away from crossing lines
        offset = size * 0.045
        if px < 0.5:
            tx -= offset
        elif px > 0.5:
            tx += offset
        if py < 0.5:
            ty += offset
        elif py > 0.5:
            ty -= offset

        # Rashi number (amber/gold)
        num_color = (
            colors.HexColor("#c2410c") if is_lagna
            else colors.HexColor("#a16207")
        )
        c.setFillColor(num_color)
        c.setFont("Helvetica-Bold", 10 if not is_lagna else 11)
        c.drawCentredString(tx, ty + 9, str(house["rashi_number"]))

        # Planet labels (one per line, each in its own color)
        line_y = ty - 2
        for p in house["planets"]:
            short_raw = p["short"]
            is_retro  = short_raw.endswith("R") and short_raw[:-1] in PLANET_FULL_NAMES
            short_key = short_raw[:-1] if is_retro else short_raw

            full_name = PLANET_FULL_NAMES.get(short_key, short_raw)
            if is_retro:
                full_name += " ℞"

            col = PLANET_COLORS.get(short_key, colors.HexColor("#111827"))
            c.setFillColor(col)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(tx, line_y, full_name)
            line_y -= 8

        # House / rashi label
        c.setFillColor(colors.HexColor("#57534e"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(tx, ty - 24, f"H{house_num} {house['rashi']}")

    # ── Lagna marker — small triangle highlight in house-1 area ──────────────
    # Draw a subtle amber dot at the lagna position centre
    lpx, lpy = HOUSE_POSITIONS[1]
    ltx = x + lpx * size
    lty = y + (1 - lpy) * size
    c.setFillColor(colors.HexColor("#fed7aa"))
    c.setStrokeColor(colors.HexColor("#c2410c"))
    c.setLineWidth(0.8)
    c.circle(ltx, lty + 9 + 16, 5, fill=1, stroke=1)

    c.restoreState()
