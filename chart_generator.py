from PIL import Image, ImageDraw, ImageFont


def generate_kundli_chart(d1_chart, output_path="kundli_chart.png"):
    img = Image.new("RGB", (600, 600), "white")
    draw = ImageDraw.Draw(img)

    # Draw outer square
    draw.rectangle((50, 50, 550, 550), outline="black", width=3)

    # Draw diagonals (North Indian style)
    draw.line((50, 50, 550, 550), fill="black", width=2)
    draw.line((550, 50, 50, 550), fill="black", width=2)

    # Mid lines
    draw.line((300, 50, 300, 550), fill="black", width=2)
    draw.line((50, 300, 550, 300), fill="black", width=2)

    # Basic font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    # Group planets by house
    house_map = {}
    for planet, pos in d1_chart.items():
        house_map.setdefault(pos["house"], []).append(planet)

    # Coordinates for houses (approx)
    coords = {
        1: (260, 260),
        2: (380, 120),
        3: (480, 260),
        4: (380, 400),
        5: (260, 480),
        6: (120, 400),
        7: (50, 260),
        8: (120, 120),
        9: (260, 50),
        10: (380, 50),
        11: (550, 260),
        12: (50, 50),
    }

    for house, planets in house_map.items():
        text = ",".join(planets)
        x, y = coords.get(house, (300, 300))
        draw.text((x, y), text, fill="black", font=font)

    img.save(output_path)
    return output_path
