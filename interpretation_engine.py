"""
DharmaPath Kundli Interpretation Engine
Rule-based Jyotish interpretation layer.

Input:
    result dictionary from KundliEngine.calculate_all()

Output:
    List of report sections:
    [
      {"title": "...", "paragraphs": ["...", "..."]},
      ...
    ]
"""

RASHI_NATURE = {
    "Mesha": "active, bold, direct, courageous and action-oriented",
    "Vrishabha": "stable, practical, persistent, comfort-loving and grounded",
    "Mithuna": "intellectual, communicative, flexible, curious and analytical",
    "Karka": "emotional, nurturing, protective, family-oriented and intuitive",
    "Simha": "confident, expressive, royal, leadership-oriented and proud",
    "Kanya": "analytical, disciplined, service-oriented, detail-focused and practical",
    "Tula": "balanced, diplomatic, artistic, relationship-oriented and refined",
    "Vrishchika": "intense, private, transformative, emotional and research-oriented",
    "Dhanu": "philosophical, dharmic, optimistic, spiritual and knowledge-seeking",
    "Makara": "disciplined, hardworking, practical, patient and responsibility-driven",
    "Kumbha": "innovative, humanitarian, unconventional, intellectual and future-oriented",
    "Meena": "spiritual, compassionate, imaginative, sensitive and devotional",
}

HOUSE_MEANINGS = {
    1: "self, personality, body, confidence, health and life direction",
    2: "wealth, speech, family, food habits, values and accumulated resources",
    3: "courage, communication, siblings, skills, effort and short journeys",
    4: "mother, home, property, inner peace, education and emotional foundation",
    5: "intelligence, children, creativity, mantra, past-life merit and learning",
    6: "service, disease, debts, enemies, competition, discipline and daily work",
    7: "marriage, spouse, partnerships, business agreements and public dealings",
    8: "longevity, transformation, hidden matters, occult, inheritance and sudden events",
    9: "dharma, fortune, father, guru, higher knowledge, pilgrimage and blessings",
    10: "career, karma, authority, profession, status and public life",
    11: "gains, income, friends, networks, ambitions and fulfillment of desires",
    12: "expenses, sleep, foreign lands, isolation, moksha, spirituality and surrender",
}

PLANET_MEANINGS = {
    "Sun": "soul, authority, father, confidence, government, leadership and vitality",
    "Moon": "mind, emotions, mother, comfort, public connection and mental peace",
    "Mars": "energy, courage, land, siblings, conflict, engineering and action",
    "Mercury": "intellect, speech, business, communication, learning, logic and technology",
    "Jupiter": "wisdom, dharma, children, teacher, prosperity, guidance and expansion",
    "Venus": "love, marriage, beauty, luxury, arts, comforts, vehicles and pleasure",
    "Saturn": "karma, discipline, delay, responsibility, hard work, maturity and endurance",
    "Rahu": "ambition, foreign influence, technology, obsession, sudden rise and illusion",
    "Ketu": "detachment, spirituality, moksha, isolation, past karma and inner liberation",
    "Lagna": "the self, body, identity, personality and life direction",
}

DASHA_GENERAL = {
    "Sun": (
        "Sun Mahadasha may bring focus on authority, career visibility, father, "
        "confidence, leadership and self-expression. It can create recognition when "
        "well placed, but ego conflicts or pressure from authority may arise when afflicted."
    ),
    "Moon": (
        "Moon Mahadasha may emphasize emotions, family, mother, home, public image, "
        "mental peace and social connection. It can bring nurturing experiences, but "
        "also emotional sensitivity and mood fluctuations."
    ),
    "Mars": (
        "Mars Mahadasha may bring action, courage, property matters, competition, "
        "technical work, conflicts and ambition. It supports initiative, but requires "
        "control over anger and impulsive decisions."
    ),
    "Mercury": (
        "Mercury Mahadasha may bring education, communication, business, technology, "
        "writing, analysis and networking. It is generally good for learning and trade, "
        "but may create overthinking when disturbed."
    ),
    "Jupiter": (
        "Jupiter Mahadasha may bring wisdom, dharma, children, teaching, prosperity, "
        "guidance, spiritual learning and expansion. It often supports growth, ethics "
        "and blessings when Jupiter is strong."
    ),
    "Venus": (
        "Venus Mahadasha may bring relationships, marriage, comforts, luxury, creativity, "
        "vehicles, artistic growth and material enjoyment. It can be pleasant, but excess "
        "attachment to pleasure should be balanced."
    ),
    "Saturn": (
        "Saturn Mahadasha may bring discipline, responsibility, career maturity, delays, "
        "karma, endurance and long-term stability. It can feel heavy, but often builds "
        "lasting success through patience and hard work."
    ),
    "Rahu": (
        "Rahu Mahadasha may bring ambition, foreign connections, technology, unusual rise, "
        "experimentation and worldly desire. It can give sudden growth, but also confusion, "
        "restlessness or unconventional situations."
    ),
    "Ketu": (
        "Ketu Mahadasha may bring detachment, spirituality, isolation, inner search, "
        "past-life karma and liberation themes. It may reduce worldly attachment and push "
        "the native toward deeper self-understanding."
    ),
}


def get_chart(result, chart_key="d1_rashi_chart"):
    return result.get(chart_key, {})


def planet_line(planet, pos):
    retro = " retrograde" if pos.get("retrograde") and planet not in ["Rahu", "Ketu", "Lagna"] else ""
    return (
        f"{planet} is placed in {pos['rashi']} at {pos['degree_in_rashi']:.2f}° "
        f"in house {pos['house']}, in {pos['nakshatra']} nakshatra pada {pos['pada']}{retro}."
    )


def interpret_lagna(result):
    d1 = get_chart(result)
    lagna = d1["Lagna"]
    rashi = lagna["rashi"]

    paragraphs = [
        f"The Lagna is in {rashi}. This gives a {RASHI_NATURE.get(rashi, 'distinct')} personality pattern.",
        (
            f"Lagna falls at {lagna['degree_in_rashi']:.2f}° in {rashi}, in "
            f"{lagna['nakshatra']} nakshatra pada {lagna['pada']}. This point represents the native's body, "
            f"temperament, identity, health tendency and life direction."
        ),
    ]

    planets_in_first = [
        p for p, pos in d1.items()
        if pos["house"] == 1 and p != "Lagna"
    ]

    if planets_in_first:
        paragraphs.append(
            "Planets placed in the 1st house strongly influence personality. "
            f"In this chart, the 1st house contains: {', '.join(planets_in_first)}."
        )

    return {
        "title": "Lagna and Personality Analysis",
        "paragraphs": paragraphs,
    }


def interpret_houses(result):
    d1 = get_chart(result)
    sections = []

    for house in range(1, 13):
        planets = [
            p for p, pos in d1.items()
            if pos["house"] == house and p != "Lagna"
        ]

        if house == 1:
            planets = [
                p for p, pos in d1.items()
                if pos["house"] == house
            ]

        paragraphs = [
            f"The {house} house represents {HOUSE_MEANINGS[house]}."
        ]

        if planets:
            paragraphs.append(
                f"Planets influencing this house by placement: {', '.join(planets)}."
            )
            for planet in planets:
                pos = d1[planet]
                meaning = PLANET_MEANINGS.get(planet, "")
                paragraphs.append(
                    f"{planet} represents {meaning}. Since it is placed in the {house} house, "
                    f"its energy becomes connected with {HOUSE_MEANINGS[house]}."
                )
        else:
            paragraphs.append(
                "No major planet is directly placed in this house. Results will depend on the house lord, aspects and dasha periods."
            )

        sections.append({
            "title": f"Bhava {house} Interpretation",
            "paragraphs": paragraphs,
        })

    return sections


def interpret_planets(result):
    d1 = get_chart(result)
    sections = []

    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for planet in order:
        pos = d1[planet]
        paragraphs = [
            planet_line(planet, pos),
            (
                f"{planet} signifies {PLANET_MEANINGS.get(planet)}. Its placement in house {pos['house']} "
                f"connects these significations with {HOUSE_MEANINGS.get(pos['house'])}."
            ),
            (
                f"The sign {pos['rashi']} adds a {RASHI_NATURE.get(pos['rashi'], 'unique')} expression "
                f"to {planet}'s results."
            ),
        ]

        if pos.get("retrograde") and planet not in ["Rahu", "Ketu"]:
            paragraphs.append(
                f"{planet} is retrograde, which may internalize its energy and make its results more karmic, delayed or reflective."
            )

        sections.append({
            "title": f"{planet} Interpretation",
            "paragraphs": paragraphs,
        })

    return sections


def find_conjunctions(result):
    d1 = get_chart(result)
    house_map = {}

    for planet, pos in d1.items():
        house_map.setdefault(pos["house"], []).append(planet)

    paragraphs = []

    for house, planets in sorted(house_map.items()):
        if len(planets) > 1:
            paragraphs.append(
                f"House {house} contains a conjunction or combined influence of: {', '.join(planets)}. "
                f"This intensifies matters of {HOUSE_MEANINGS.get(house)}."
            )

            for i in range(len(planets)):
                for j in range(i + 1, len(planets)):
                    p1, p2 = planets[i], planets[j]
                    deg1 = d1[p1]["degree_in_rashi"]
                    deg2 = d1[p2]["degree_in_rashi"]
                    diff = abs(deg1 - deg2)
                    strength = "very strong" if diff <= 5 else "strong" if diff <= 10 else "moderate" if diff <= 15 else "mild"
                    paragraphs.append(
                        f"{p1} and {p2} are about {diff:.2f}° apart in the same house/sign, giving a {strength} conjunction effect."
                    )

    if not paragraphs:
        paragraphs.append("No major same-house conjunctions are present among the primary planets.")

    return {
        "title": "Conjunction Analysis",
        "paragraphs": paragraphs,
    }


def find_special_aspects(result):
    d1 = get_chart(result)
    paragraphs = []

    aspect_rules = {
        "Mars": [4, 7, 8],
        "Jupiter": [5, 7, 9],
        "Saturn": [3, 7, 10],
        "Rahu": [5, 7, 9],
        "Ketu": [5, 7, 9],
    }

    for planet, aspects in aspect_rules.items():
        if planet not in d1:
            continue

        from_house = d1[planet]["house"]

        for aspect in aspects:
            target_house = ((from_house + aspect - 2) % 12) + 1
            paragraphs.append(
                f"{planet} from house {from_house} aspects house {target_house}. "
                f"This influences matters of {HOUSE_MEANINGS.get(target_house)}."
            )

    return {
        "title": "Drishti / Aspect Analysis",
        "paragraphs": paragraphs,
    }


def interpret_d9(result):
    d9 = get_chart(result, "d9_navamsa_chart")
    d1 = get_chart(result, "d1_rashi_chart")

    paragraphs = [
        "D9 Navamsa is used to understand dharma, inner maturity, marriage potential, spouse-related themes and deeper planetary strength.",
        "A planet strong in D9 may improve its results over time, even if its D1 placement appears challenging.",
    ]

    for planet in ["Lagna", "Venus", "Jupiter", "Saturn", "Moon"]:
        if planet in d9:
            pos = d9[planet]
            paragraphs.append(
                f"In D9, {planet} is in {pos['rashi']} house {pos['house']}. "
                f"This adds a {RASHI_NATURE.get(pos['rashi'], 'specific')} inner expression."
            )

    return {
        "title": "D9 Navamsa Interpretation",
        "paragraphs": paragraphs,
    }


def interpret_mahadashas(result):
    d1 = get_chart(result)
    dashas = result.get("vimshottari_mahadasha", [])
    paragraphs = []

    for dasha in dashas:
        lord = dasha["lord"]
        pos = d1.get(lord)

        text = (
            f"{lord} Mahadasha runs from {dasha['start']} to {dasha['end']} "
            f"for approximately {dasha['years']} years. {DASHA_GENERAL.get(lord, '')}"
        )

        if pos:
            text += (
                f" In this chart, {lord} is placed in {pos['rashi']} in house {pos['house']}, "
                f"in {pos['nakshatra']} nakshatra pada {pos['pada']}. Therefore this period may strongly activate "
                f"{HOUSE_MEANINGS.get(pos['house'])}."
            )

        paragraphs.append(text)

    return {
        "title": "Vimshottari Mahadasha Life Themes",
        "paragraphs": paragraphs,
    }


def interpret_career(result):
    d1 = get_chart(result)
    career_planets = []

    for planet, pos in d1.items():
        if pos["house"] in [2, 6, 10, 11]:
            career_planets.append((planet, pos))

    paragraphs = [
        "Career is mainly studied from the 10th house, along with the 2nd house of income, 6th house of service and 11th house of gains."
    ]

    if career_planets:
        for planet, pos in career_planets:
            paragraphs.append(
                f"{planet} influences career/income matters by being placed in house {pos['house']} "
                f"({HOUSE_MEANINGS[pos['house']]})."
            )
    else:
        paragraphs.append(
            "There are no major planets directly in the 2nd, 6th, 10th or 11th houses. Career interpretation should focus more on house lords and dashas."
        )

    return {
        "title": "Career and Work Direction",
        "paragraphs": paragraphs,
    }


def interpret_relationships(result):
    d1 = get_chart(result)
    d9 = get_chart(result, "d9_navamsa_chart")

    paragraphs = [
        "Marriage and relationships are primarily studied from the 7th house, Venus, Jupiter and the D9 Navamsa chart."
    ]

    seventh_planets = [
        planet for planet, pos in d1.items()
        if pos["house"] == 7
    ]

    if seventh_planets:
        paragraphs.append(
            f"The 7th house contains: {', '.join(seventh_planets)}. This directly influences partnership and marriage themes."
        )
    else:
        paragraphs.append(
            "The 7th house has no major planet directly placed in it. Relationship results depend more on the 7th lord, Venus/Jupiter and dasha timing."
        )

    if "Venus" in d1:
        v = d1["Venus"]
        paragraphs.append(
            f"Venus is in {v['rashi']} house {v['house']}, showing relationship style, comforts, attraction and harmony themes."
        )

    if "Venus" in d9:
        v9 = d9["Venus"]
        paragraphs.append(
            f"In D9, Venus is in {v9['rashi']} house {v9['house']}, adding deeper relationship and marriage maturity indicators."
        )

    return {
        "title": "Marriage and Relationship Indications",
        "paragraphs": paragraphs,
    }


def interpret_spirituality(result):
    d1 = get_chart(result)

    spiritual_planets = []
    for planet, pos in d1.items():
        if pos["house"] in [5, 8, 9, 12] or planet in ["Jupiter", "Ketu"]:
            spiritual_planets.append((planet, pos))

    paragraphs = [
        "Spiritual tendencies are studied from the 5th house of mantra, 8th house of occult depth, 9th house of dharma and 12th house of moksha."
    ]

    for planet, pos in spiritual_planets:
        paragraphs.append(
            f"{planet} connects with spiritual themes through house {pos['house']} or its natural significations. "
            f"This may influence {HOUSE_MEANINGS.get(pos['house'])}."
        )

    return {
        "title": "Spiritual and Dharma Indications",
        "paragraphs": paragraphs,
    }


def generate_interpretation_report(result):
    sections = []

    sections.append({
        "title": "Important Note",
        "paragraphs": [
            "This report is generated through a rule-based Jyotish interpretation engine. It is intended for spiritual guidance, self-reflection and educational use.",
            "Predictions should not be treated as guaranteed events. Free will, karma, environment and personal choices also shape life outcomes.",
        ],
    })

    sections.append(interpret_lagna(result))
    sections.extend(interpret_houses(result))
    sections.extend(interpret_planets(result))
    sections.append(find_conjunctions(result))
    sections.append(find_special_aspects(result))
    sections.append(interpret_d9(result))
    sections.append(interpret_career(result))
    sections.append(interpret_relationships(result))
    sections.append(interpret_spirituality(result))
    sections.append(interpret_mahadashas(result))

    return sections