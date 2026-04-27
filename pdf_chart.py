from reportlab.lib import colors


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

PLANET_FULL_NAMES = {
    "La": "Lagna",
    "Su": "Sun / Surya",
    "Mo": "Moon / Chandra",
    "Ma": "Mars / Mangal",
    "Me": "Mercury / Budh",
    "Ju": "Jupiter / Guru",
    "Ve": "Venus / Shukra",
    "Sa": "Saturn / Shani",
    "Ra": "Rahu",
    "Ke": "Ketu",
}


def draw_north_indian_chart(c, chart_visual, x, y, size, title="D1 Rashi Chart"):
    """
    Draws a professional North Indian kundli directly into PDF.
    x, y = bottom-left position.
    size = chart width/height.
    """

    c.saveState()

    # Background
    c.setFillColor(colors.HexColor("#fffaf0"))
    c.rect(x, y, size, size, fill=1, stroke=0)

    # Border and lines
    c.setStrokeColor(colors.HexColor("#7c2d12"))
    c.setLineWidth(2.2)

    # Outer square
    c.rect(x, y, size, size, fill=0, stroke=1)

    # Main diagonals
    c.line(x, y + size, x + size, y)
    c.line(x, y, x + size, y + size)

    # Inner diamond lines
    c.line(x + size / 2, y + size, x + size, y + size / 2)
    c.line(x + size, y + size / 2, x + size / 2, y)
    c.line(x + size / 2, y, x, y + size / 2)
    c.line(x, y + size / 2, x + size / 2, y + size)

    # Title
    c.setFillColor(colors.HexColor("#7c2d12"))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + size / 2, y + size + 14, title)

    houses = chart_visual["houses"]

    for house_num in range(1, 13):
        house = houses[str(house_num)]
        px, py = HOUSE_POSITIONS[house_num]

        tx = x + px * size
        ty = y + (1 - py) * size

        # Move text away from chart crossing lines
        offset = size * 0.045

        if px < 0.5:
            tx -= offset
        elif px > 0.5:
            tx += offset

        if py < 0.5:
            ty += offset
        elif py > 0.5:
            ty -= offset
        #planets = " ".join([p["short"] for p in house["planets"]])
        planet_lines = [
            PLANET_FULL_NAMES.get(p["short"].replace("R", ""), p["short"])
            for p in house["planets"]
        ]

        # Rashi number
        c.setFillColor(colors.HexColor("#a16207"))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(tx, ty + 9, str(house["rashi_number"]))

        # Planets
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold", 6.5)
        #c.drawCentredString(tx, ty - 3, planets)
        line_y = ty - 3
        for planet_text in planet_lines:
            c.drawCentredString(tx, line_y, planet_text)
            line_y -= 8


        # House/rashi name
        c.setFillColor(colors.HexColor("#57534e"))
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(tx, ty - 22, f"H{house_num} {house['rashi']}")

    c.restoreState()
