from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import swisseph as swe

BASE_DIR = Path(__file__).resolve().parent
EPHE_DIR = BASE_DIR / "ephe"

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASHI_HINDI = [
    "Mesh", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

# ── Lookup tables ─────────────────────────────────────────────────────────────

# Varna by Rashi (Moon sign)
RASHI_VARNA = {
    0: "Kshatriya", 1: "Vaishya",   2: "Shudra",    3: "Brahmin",
    4: "Kshatriya", 5: "Vaishya",   6: "Shudra",    7: "Brahmin",
    8: "Kshatriya", 9: "Vaishya",  10: "Shudra",   11: "Brahmin",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vashya by Rashi
RASHI_VASHYA = {
    0: "Chatushpad", 1: "Chatushpad", 2: "Manav",    3: "Jalachar",
    4: "Vanchar",    5: "Manav",      6: "Manav",    7: "Keeta",
    8: "Manav",      9: "Jalachar",  10: "Manav",   11: "Jalachar",
}
# (controller, controlled) → True means controller gets 2 pts when girl controls boy
_VASHYA_CONTROLS = {
    ("Manav", "Chatushpad"), ("Manav", "Vanchar"),
    ("Chatushpad", "Jalachar"), ("Vanchar", "Jalachar"),
}

# Gana by Nakshatra index
NAK_GANA = [
    "Deva",     # 0  Ashwini
    "Manav",    # 1  Bharani
    "Rakshasa", # 2  Krittika
    "Manav",    # 3  Rohini
    "Deva",     # 4  Mrigashira
    "Manav",    # 5  Ardra
    "Deva",     # 6  Punarvasu
    "Deva",     # 7  Pushya
    "Rakshasa", # 8  Ashlesha
    "Rakshasa", # 9  Magha
    "Manav",    # 10 Purva Phalguni
    "Manav",    # 11 Uttara Phalguni
    "Deva",     # 12 Hasta
    "Rakshasa", # 13 Chitra
    "Deva",     # 14 Swati
    "Rakshasa", # 15 Vishakha
    "Deva",     # 16 Anuradha
    "Rakshasa", # 17 Jyeshtha
    "Rakshasa", # 18 Mula
    "Manav",    # 19 Purva Ashadha
    "Manav",    # 20 Uttara Ashadha
    "Deva",     # 21 Shravana
    "Rakshasa", # 22 Dhanishtha
    "Rakshasa", # 23 Shatabhisha
    "Manav",    # 24 Purva Bhadrapada
    "Manav",    # 25 Uttara Bhadrapada
    "Deva",     # 26 Revati
]

# Nadi by Nakshatra index
NAK_NADI = [
    "Adi",    # 0  Ashwini
    "Madhya", # 1  Bharani
    "Antya",  # 2  Krittika
    "Antya",  # 3  Rohini
    "Madhya", # 4  Mrigashira
    "Adi",    # 5  Ardra
    "Adi",    # 6  Punarvasu
    "Madhya", # 7  Pushya
    "Antya",  # 8  Ashlesha
    "Antya",  # 9  Magha
    "Madhya", # 10 Purva Phalguni
    "Adi",    # 11 Uttara Phalguni
    "Adi",    # 12 Hasta
    "Madhya", # 13 Chitra
    "Antya",  # 14 Swati
    "Antya",  # 15 Vishakha
    "Madhya", # 16 Anuradha
    "Adi",    # 17 Jyeshtha
    "Adi",    # 18 Mula
    "Madhya", # 19 Purva Ashadha
    "Antya",  # 20 Uttara Ashadha
    "Antya",  # 21 Shravana
    "Madhya", # 22 Dhanishtha
    "Adi",    # 23 Shatabhisha
    "Adi",    # 24 Purva Bhadrapada
    "Madhya", # 25 Uttara Bhadrapada
    "Antya",  # 26 Revati
]

# Yoni by Nakshatra index
NAK_YONI = [
    "Horse",    # 0  Ashwini
    "Elephant", # 1  Bharani
    "Goat",     # 2  Krittika
    "Serpent",  # 3  Rohini
    "Serpent",  # 4  Mrigashira
    "Dog",      # 5  Ardra
    "Cat",      # 6  Punarvasu
    "Goat",     # 7  Pushya
    "Cat",      # 8  Ashlesha
    "Rat",      # 9  Magha
    "Rat",      # 10 Purva Phalguni
    "Cow",      # 11 Uttara Phalguni
    "Buffalo",  # 12 Hasta
    "Tiger",    # 13 Chitra
    "Buffalo",  # 14 Swati
    "Tiger",    # 15 Vishakha
    "Deer",     # 16 Anuradha
    "Deer",     # 17 Jyeshtha
    "Dog",      # 18 Mula
    "Monkey",   # 19 Purva Ashadha
    "Mongoose", # 20 Uttara Ashadha
    "Monkey",   # 21 Shravana
    "Lion",     # 22 Dhanishtha
    "Horse",    # 23 Shatabhisha
    "Lion",     # 24 Purva Bhadrapada
    "Cow",      # 25 Uttara Bhadrapada
    "Elephant", # 26 Revati
]

YONI_ENEMIES = {
    frozenset(["Horse",    "Buffalo"]),
    frozenset(["Elephant", "Lion"]),
    frozenset(["Goat",     "Monkey"]),
    frozenset(["Dog",      "Deer"]),
    frozenset(["Cat",      "Rat"]),
    frozenset(["Cow",      "Tiger"]),
    frozenset(["Serpent",  "Mongoose"]),
}

# Rashi lord
RASHI_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
    5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
    9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

# Natural planet relationships (from p1's perspective to p2)
# F=Friend, N=Neutral, E=Enemy
_PR = {
    ("Sun",     "Moon"):    "F", ("Sun",     "Mars"):    "F",
    ("Sun",     "Mercury"): "N", ("Sun",     "Jupiter"): "F",
    ("Sun",     "Venus"):   "E", ("Sun",     "Saturn"):  "E",
    ("Moon",    "Sun"):     "F", ("Moon",    "Mars"):    "N",
    ("Moon",    "Mercury"): "F", ("Moon",    "Jupiter"): "N",
    ("Moon",    "Venus"):   "N", ("Moon",    "Saturn"):  "N",
    ("Mars",    "Sun"):     "F", ("Mars",    "Moon"):    "F",
    ("Mars",    "Mercury"): "E", ("Mars",    "Jupiter"): "F",
    ("Mars",    "Venus"):   "N", ("Mars",    "Saturn"):  "N",
    ("Mercury", "Sun"):     "N", ("Mercury", "Moon"):    "E",
    ("Mercury", "Mars"):    "N", ("Mercury", "Jupiter"): "N",
    ("Mercury", "Venus"):   "F", ("Mercury", "Saturn"):  "N",
    ("Jupiter", "Sun"):     "F", ("Jupiter", "Moon"):    "F",
    ("Jupiter", "Mars"):    "F", ("Jupiter", "Mercury"): "E",
    ("Jupiter", "Venus"):   "E", ("Jupiter", "Saturn"):  "N",
    ("Venus",   "Sun"):     "E", ("Venus",   "Moon"):    "N",
    ("Venus",   "Mars"):    "N", ("Venus",   "Mercury"): "F",
    ("Venus",   "Jupiter"): "E", ("Venus",   "Saturn"):  "F",
    ("Saturn",  "Sun"):     "E", ("Saturn",  "Moon"):    "E",
    ("Saturn",  "Mars"):    "E", ("Saturn",  "Mercury"): "N",
    ("Saturn",  "Jupiter"): "N", ("Saturn",  "Venus"):   "F",
}


# ── Moon position ─────────────────────────────────────────────────────────────

def get_birth_moon(birth_date: str, birth_time: str, tz_offset: float) -> Dict:
    """Return Moon's sidereal longitude and derived factors."""
    if EPHE_DIR.exists():
        swe.set_ephe_path(str(EPHE_DIR))
    else:
        swe.set_ephe_path(str(BASE_DIR))
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    dt  = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    utc = dt - timedelta(hours=tz_offset)
    jd  = swe.julday(utc.year, utc.month, utc.day,
                     utc.hour + utc.minute / 60.0, swe.GREG_CAL)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    try:
        m, _ = swe.calc_ut(jd, swe.MOON, flags)
    except Exception:
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)

    moon_lon  = m[0] % 360
    nak_idx   = int(moon_lon / (360 / 27))
    rashi_idx = int(moon_lon / 30)
    pada      = int((moon_lon % (360 / 27)) / (360 / 108)) + 1

    return {
        "moon_lon":  moon_lon,
        "nak_idx":   nak_idx,
        "nak_name":  NAKSHATRAS[nak_idx],
        "pada":      pada,
        "rashi_idx": rashi_idx,
        "rashi":     RASHIS[rashi_idx],
        "rashi_hindi": RASHI_HINDI[rashi_idx],
    }


# ── Individual Koota scorers ──────────────────────────────────────────────────

def _varna(boy: Dict, girl: Dict) -> Dict:
    bv = RASHI_VARNA[boy["rashi_idx"]]
    gv = RASHI_VARNA[girl["rashi_idx"]]
    score = 1 if VARNA_RANK[bv] >= VARNA_RANK[gv] else 0
    return {
        "name": "Varna", "max": 1, "score": score,
        "p1_value": bv, "p2_value": gv,
        "quality": "good" if score else "bad",
        "detail": "Boy's Varna is equal or higher — harmonious" if score
                  else "Boy's Varna is lower than girl's — mismatch",
    }


def _vashya(boy: Dict, girl: Dict) -> Dict:
    bv = RASHI_VASHYA[boy["rashi_idx"]]
    gv = RASHI_VASHYA[girl["rashi_idx"]]
    if bv == gv:
        score, detail = 2, "Same Vashya group — mutual attraction"
    elif frozenset([bv, gv]) in {frozenset(p) for p in _VASHYA_CONTROLS}:
        score, detail = 1, "Compatible Vashya groups — partial harmony"
    else:
        score, detail = 0, "Incompatible Vashya groups"
    return {
        "name": "Vashya", "max": 2, "score": score,
        "p1_value": bv, "p2_value": gv,
        "quality": "good" if score == 2 else ("neutral" if score == 1 else "bad"),
        "detail": detail,
    }


_TARA_NAMES = ["", "Janma", "Sampat", "Vipat", "Kshema",
               "Pratyari", "Sadhaka", "Vadha", "Mitra", "Ati-mitra"]
_TARA_INAUSPICIOUS = {1, 3, 5, 7}  # Janma, Vipat, Pratyari, Vadha


def _tara(boy: Dict, girl: Dict) -> Dict:
    gn = girl["nak_idx"] + 1  # 1-indexed
    bn = boy["nak_idx"] + 1

    def _tnum(src: int, tgt: int) -> int:
        raw = ((tgt - src) % 27) + 1
        t = raw % 9
        return t if t != 0 else 9

    gb_t = _tnum(gn, bn)   # boy's Nakshatra counted from girl → Tara for boy
    bg_t = _tnum(bn, gn)   # girl's Nakshatra counted from boy → Tara for girl

    gb_ok = gb_t not in _TARA_INAUSPICIOUS
    bg_ok = bg_t not in _TARA_INAUSPICIOUS

    if gb_ok and bg_ok:
        score, quality = 3, "good"
        detail = "Both Tara counts are auspicious"
    elif gb_ok or bg_ok:
        score, quality = 1, "neutral"
        detail = "One Tara count is inauspicious — partial compatibility"
    else:
        score, quality = 0, "bad"
        detail = "Both Tara counts are inauspicious"

    return {
        "name": "Tara", "max": 3, "score": score,
        "p1_value": f"{_TARA_NAMES[gb_t]} ({'Auspicious' if gb_ok else 'Inauspicious'})",
        "p2_value": f"{_TARA_NAMES[bg_t]} ({'Auspicious' if bg_ok else 'Inauspicious'})",
        "quality": quality, "detail": detail,
    }


def _yoni(boy: Dict, girl: Dict) -> Dict:
    by_ = NAK_YONI[boy["nak_idx"]]
    gy  = NAK_YONI[girl["nak_idx"]]
    if by_ == gy:
        score, quality, detail = 4, "good", "Same Yoni — excellent physical compatibility"
    elif frozenset([by_, gy]) in YONI_ENEMIES:
        score, quality, detail = 0, "bad", "Enemy Yoni — physical incompatibility"
    else:
        score, quality, detail = 2, "neutral", "Neutral Yoni — average compatibility"
    return {
        "name": "Yoni", "max": 4, "score": score,
        "p1_value": by_, "p2_value": gy,
        "quality": quality, "detail": detail,
    }


def _graha_maitri(boy: Dict, girl: Dict) -> Dict:
    bl = RASHI_LORD[boy["rashi_idx"]]
    gl = RASHI_LORD[girl["rashi_idx"]]
    if bl == gl:
        score, quality = 5, "good"
        detail = f"Same lord ({bl}) — excellent mental compatibility"
    else:
        r12 = _PR.get((bl, gl), "N")
        r21 = _PR.get((gl, bl), "N")
        pair = (r12, r21)
        if pair == ("F", "F"):
            score, quality, detail = 5, "good", "Mutual friends — excellent mental harmony"
        elif pair in [("F", "N"), ("N", "F")]:
            score, quality, detail = 4, "good", "Friend + Neutral — good compatibility"
        elif pair == ("N", "N"):
            score, quality, detail = 3, "neutral", "Both neutral — average mental compatibility"
        elif pair in [("F", "E"), ("E", "F")]:
            score, quality, detail = 1, "neutral", "Friend + Enemy — mixed compatibility"
        else:
            score, quality, detail = 0, "bad", "Enemy lords — mental friction likely"
    return {
        "name": "Graha Maitri", "max": 5, "score": score,
        "p1_value": f"{RASHIS[boy['rashi_idx']]} (Lord: {bl})",
        "p2_value": f"{RASHIS[girl['rashi_idx']]} (Lord: {gl})",
        "quality": quality, "detail": detail,
    }


def _gana(boy: Dict, girl: Dict) -> Dict:
    bg = NAK_GANA[boy["nak_idx"]]
    gg = NAK_GANA[girl["nak_idx"]]
    if bg == gg:
        score, quality, detail = 6, "good", f"Both {bg} Gana — excellent temperament match"
    elif {bg, gg} == {"Deva", "Manav"}:
        score, quality, detail = 5, "good", "Deva + Manav — compatible natures"
    elif {bg, gg} == {"Manav", "Rakshasa"}:
        score, quality, detail = 1, "bad", "Manav + Rakshasa — Gana Dosha present"
    else:
        score, quality, detail = 0, "bad", "Deva + Rakshasa — Gana Dosha (serious mismatch)"
    return {
        "name": "Gana", "max": 6, "score": score,
        "p1_value": bg, "p2_value": gg,
        "quality": quality, "detail": detail,
        "dosha": score <= 1,
    }


def _bhakoot(boy: Dict, girl: Dict) -> Dict:
    br = boy["rashi_idx"] + 1   # 1-indexed
    gr = girl["rashi_idx"] + 1
    gb = ((br - gr) % 12) + 1
    bg = ((gr - br) % 12) + 1
    dosha_pairs = {(2, 12), (12, 2), (5, 9), (9, 5), (6, 8), (8, 6)}
    dosha = (gb, bg) in dosha_pairs
    score = 0 if dosha else 7
    quality = "bad" if dosha else "good"
    detail = (f"Bhakoot Dosha ({gb}-{bg}) — can affect family welfare"
              if dosha else "No Bhakoot Dosha — good family compatibility")
    return {
        "name": "Bhakoot", "max": 7, "score": score,
        "p1_value": RASHIS[boy["rashi_idx"]], "p2_value": RASHIS[girl["rashi_idx"]],
        "quality": quality, "detail": detail,
        "dosha": dosha,
    }


def _nadi(boy: Dict, girl: Dict) -> Dict:
    bn = NAK_NADI[boy["nak_idx"]]
    gn = NAK_NADI[girl["nak_idx"]]
    dosha = (bn == gn)
    score = 0 if dosha else 8
    quality = "bad" if dosha else "good"
    detail = (f"Nadi Dosha — both {bn} Nadi. Health and progeny concerns."
              if dosha else f"Different Nadi ({bn} & {gn}) — no Nadi Dosha")
    return {
        "name": "Nadi", "max": 8, "score": score,
        "p1_value": bn, "p2_value": gn,
        "quality": quality, "detail": detail,
        "dosha": dosha,
    }


# ── Main function ─────────────────────────────────────────────────────────────

def calculate_milan(
    boy_date: str, boy_time: str, boy_tz: float, boy_name: str,
    girl_date: str, girl_time: str, girl_tz: float, girl_name: str,
) -> Dict:
    boy  = get_birth_moon(boy_date,  boy_time,  boy_tz)
    girl = get_birth_moon(girl_date, girl_time, girl_tz)

    kootas = [
        _varna(boy, girl),
        _vashya(boy, girl),
        _tara(boy, girl),
        _yoni(boy, girl),
        _graha_maitri(boy, girl),
        _gana(boy, girl),
        _bhakoot(boy, girl),
        _nadi(boy, girl),
    ]

    total = sum(k["score"] for k in kootas)
    max_score = 36

    doshas = [k["name"] for k in kootas if k.get("dosha")]

    if total >= 32:
        rating, rating_class = "Excellent", "excellent"
        summary = "Highly auspicious alliance. Strong compatibility across all factors."
    elif total >= 28:
        rating, rating_class = "Very Good", "good"
        summary = "Very good compatibility. A harmonious and balanced alliance."
    elif total >= 24:
        rating, rating_class = "Good", "good"
        summary = "Good compatibility. Minor challenges can be resolved with understanding."
    elif total >= 18:
        rating, rating_class = "Average", "neutral"
        summary = "Average compatibility. Careful consideration advised before proceeding."
    else:
        rating, rating_class = "Below Average", "bad"
        summary = "Compatibility is below the recommended threshold. Seek expert guidance."

    return {
        "boy":  {**boy,  "name": boy_name},
        "girl": {**girl, "name": girl_name},
        "total_score": total,
        "max_score":   max_score,
        "rating":      rating,
        "rating_class": rating_class,
        "summary":     summary,
        "kootas":      kootas,
        "doshas":      doshas,
    }
