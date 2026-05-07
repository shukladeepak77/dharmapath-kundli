from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import swisseph as swe

BASE_DIR = Path(__file__).resolve().parent
EPHE_DIR = BASE_DIR / "ephe"

TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

TITHI_PAKSHA = ["Shukla"] * 15 + ["Krishna"] * 15

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
] * 3

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarman", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
    "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
    "Brahma", "Indra", "Vaidhriti",
]

YOGA_QUALITY = {
    "Vishkambha": "inauspicious", "Priti": "auspicious", "Ayushman": "auspicious",
    "Saubhagya": "auspicious", "Shobhana": "auspicious", "Atiganda": "inauspicious",
    "Sukarman": "auspicious", "Dhriti": "auspicious", "Shula": "inauspicious",
    "Ganda": "inauspicious", "Vriddhi": "auspicious", "Dhruva": "auspicious",
    "Vyaghata": "inauspicious", "Harshana": "auspicious", "Vajra": "inauspicious",
    "Siddhi": "auspicious", "Vyatipata": "inauspicious", "Variyan": "neutral",
    "Parigha": "inauspicious", "Shiva": "auspicious", "Siddha": "auspicious",
    "Sadhya": "auspicious", "Shubha": "auspicious", "Shukla": "auspicious",
    "Brahma": "auspicious", "Indra": "auspicious", "Vaidhriti": "inauspicious",
}

MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
VARA_HINDI = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"]

# 1-indexed part of the day (8 parts sunrise→sunset) for each weekday 0=Sun..6=Sat
RAHU_KAAL_PART  = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 3, 6: 4}
YAMGANDAM_PART  = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}
GULIKAI_PART    = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}

# Day Choghadiya sequence per weekday (0=Sun)
DAY_CHOGHADIYA = {
    0: ["Udvega", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udvega"],
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udvega", "Char", "Labh", "Amrit"],
    2: ["Rog", "Udvega", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udvega", "Char", "Labh"],
    4: ["Shubh", "Rog", "Udvega", "Char", "Labh", "Amrit", "Kaal", "Shubh"],
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udvega", "Char"],
    6: ["Kaal", "Shubh", "Rog", "Udvega", "Char", "Labh", "Amrit", "Kaal"],
}

NIGHT_CHOGHADIYA = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udvega", "Shubh"],
    1: ["Char", "Rog", "Kaal", "Labh", "Udvega", "Shubh", "Amrit", "Char"],
    2: ["Kaal", "Labh", "Udvega", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
    3: ["Udvega", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udvega"],
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udvega", "Shubh", "Amrit"],
    5: ["Rog", "Kaal", "Labh", "Udvega", "Shubh", "Amrit", "Char", "Rog"],
    6: ["Labh", "Udvega", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],
}

CHOGHADIYA_QUALITY = {
    "Amrit": "excellent", "Shubh": "good", "Labh": "good",
    "Char": "neutral", "Udvega": "bad", "Kaal": "bad", "Rog": "bad",
}

CHOGHADIYA_MEANING = {
    "Amrit": "Nectar — highly auspicious for all works",
    "Shubh": "Auspicious — good for all activities",
    "Labh": "Profit — good for business and trade",
    "Char": "Movement — good for travel",
    "Udvega": "Anxiety — avoid important tasks",
    "Kaal": "Inauspicious — avoid new beginnings",
    "Rog": "Disease — avoid health and medical matters",
}


def _jd_to_local_time(jd: float, tz_offset: float) -> str:
    jd_epoch = datetime(4713, 11, 24, 12, 0, 0)  # Julian Day 0 = noon 4713 BC
    utc_dt = datetime(2000, 1, 1, 12, 0) + timedelta(days=jd - 2451545.0)
    local_dt = utc_dt + timedelta(hours=tz_offset)
    return local_dt.strftime("%I:%M %p")


def _jd_to_datetime(jd: float, tz_offset: float) -> datetime:
    utc_dt = datetime(2000, 1, 1, 12, 0) + timedelta(days=jd - 2451545.0)
    return utc_dt + timedelta(hours=tz_offset)


def _time_window(start_jd: float, end_jd: float, tz_offset: float) -> Dict:
    return {
        "start": _jd_to_local_time(start_jd, tz_offset),
        "end": _jd_to_local_time(end_jd, tz_offset),
    }


def calculate_panchang(
    date_str: str,
    lat: float,
    lng: float,
    tz_offset: float,
    place: str = "",
) -> Dict:
    if EPHE_DIR.exists():
        swe.set_ephe_path(str(EPHE_DIR))
    else:
        swe.set_ephe_path(str(BASE_DIR))

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    date = datetime.strptime(date_str, "%Y-%m-%d")
    # Use local noon → convert to UTC for JD
    local_noon = date.replace(hour=12, minute=0, second=0)
    utc_noon = local_noon - timedelta(hours=tz_offset)
    jd = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day,
                    utc_noon.hour + utc_noon.minute / 60.0, swe.GREG_CAL)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    try:
        sun_res, _ = swe.calc_ut(jd, swe.SUN, flags)
    except Exception:
        sun_res, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
    try:
        moon_res, _ = swe.calc_ut(jd, swe.MOON, flags)
    except Exception:
        moon_res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)

    sun_lon = sun_res[0] % 360
    moon_lon = moon_res[0] % 360

    # ── Tithi ────────────────────────────────────────────────────────────────
    diff = (moon_lon - sun_lon) % 360
    tithi_idx = int(diff / 12)  # 0–29
    tithi_name = TITHIS[tithi_idx]
    tithi_paksha = TITHI_PAKSHA[tithi_idx]
    tithi_num = (tithi_idx % 15) + 1

    # ── Nakshatra (Moon) ──────────────────────────────────────────────────────
    nak_idx = int(moon_lon / (360 / 27))
    nak_name = NAKSHATRAS[nak_idx]
    nak_lord = NAKSHATRA_LORDS[nak_idx]
    nak_pada = int((moon_lon % (360 / 27)) / (360 / 108)) + 1

    # ── Yoga ─────────────────────────────────────────────────────────────────
    yoga_idx = int(((sun_lon + moon_lon) % 360) / (360 / 27))
    yoga_name = YOGAS[yoga_idx]
    yoga_quality = YOGA_QUALITY.get(yoga_name, "neutral")

    # ── Karana ───────────────────────────────────────────────────────────────
    half_tithi = int(diff / 6)  # 0–59
    if half_tithi == 0:
        karana_name = "Kimstughna"
    elif 1 <= half_tithi <= 56:
        karana_name = MOVABLE_KARANAS[(half_tithi - 1) % 7]
    elif half_tithi == 57:
        karana_name = "Shakuni"
    elif half_tithi == 58:
        karana_name = "Chatushpada"
    else:
        karana_name = "Naga"

    # ── Vara ─────────────────────────────────────────────────────────────────
    # weekday 0=Mon in Python; convert to 0=Sun
    py_wd = date.weekday()  # 0=Mon
    sun_wd = (py_wd + 1) % 7  # 0=Sun
    vara_name = VARAS[sun_wd]
    vara_hindi = VARA_HINDI[sun_wd]
    vara_lord = VARA_LORDS[sun_wd]

    # ── Sunrise / Sunset ─────────────────────────────────────────────────────
    geopos = (lng, lat, 0.0)
    rsmi_rise = swe.CALC_RISE | swe.BIT_DISC_CENTER
    rsmi_set  = swe.CALC_SET  | swe.BIT_DISC_CENTER

    try:
        _, tret_rise = swe.rise_trans(jd - 0.5, swe.SUN, rsmi_rise, geopos, 0, 0, swe.FLG_SWIEPH)
        jd_sunrise = tret_rise[0]
    except Exception:
        jd_sunrise = jd - 0.25

    try:
        _, tret_set = swe.rise_trans(jd_sunrise, swe.SUN, rsmi_set, geopos, 0, 0, swe.FLG_SWIEPH)
        jd_sunset = tret_set[0]
    except Exception:
        jd_sunset = jd + 0.25

    sunrise_str = _jd_to_local_time(jd_sunrise, tz_offset)
    sunset_str  = _jd_to_local_time(jd_sunset,  tz_offset)

    day_dur = jd_sunset - jd_sunrise  # in days
    part    = day_dur / 8

    def day_window(part_num: int) -> Dict:
        s = jd_sunrise + (part_num - 1) * part
        return _time_window(s, s + part, tz_offset)

    # ── Rahu Kaal / Yamgandam / Gulikai ──────────────────────────────────────
    rahu_kaal  = day_window(RAHU_KAAL_PART[sun_wd])
    yamgandam  = day_window(YAMGANDAM_PART[sun_wd])
    gulikai    = day_window(GULIKAI_PART[sun_wd])

    # ── Abhijit Muhurat ───────────────────────────────────────────────────────
    solar_noon  = (jd_sunrise + jd_sunset) / 2
    muhurat_dur = day_dur / 15
    abhijit = _time_window(solar_noon - muhurat_dur / 2,
                           solar_noon + muhurat_dur / 2, tz_offset)

    # ── Choghadiya ────────────────────────────────────────────────────────────
    try:
        _, tret_rise_next = swe.rise_trans(jd_sunset, swe.SUN, rsmi_rise, geopos, 0, 0, swe.FLG_SWIEPH)
        jd_next_sunrise = tret_rise_next[0]
    except Exception:
        jd_next_sunrise = jd_sunrise + 1.0

    night_dur  = jd_next_sunrise - jd_sunset
    day_part   = day_dur  / 8
    night_part = night_dur / 8

    day_cho = []
    for i, name in enumerate(DAY_CHOGHADIYA[sun_wd]):
        s = jd_sunrise + i * day_part
        day_cho.append({
            "name": name,
            "quality": CHOGHADIYA_QUALITY[name],
            "meaning": CHOGHADIYA_MEANING[name],
            **_time_window(s, s + day_part, tz_offset),
        })

    night_cho = []
    for i, name in enumerate(NIGHT_CHOGHADIYA[sun_wd]):
        s = jd_sunset + i * night_part
        night_cho.append({
            "name": name,
            "quality": CHOGHADIYA_QUALITY[name],
            "meaning": CHOGHADIYA_MEANING[name],
            **_time_window(s, s + night_part, tz_offset),
        })

    return {
        "date": date_str,
        "place": place,
        "latitude": lat,
        "longitude": lng,
        "timezone_offset": tz_offset,
        "sunrise": sunrise_str,
        "sunset": sunset_str,
        "panchang": {
            "tithi": {
                "number": tithi_num,
                "name": tithi_name,
                "paksha": tithi_paksha,
                "display": f"{tithi_paksha} {tithi_name} ({tithi_num})",
            },
            "nakshatra": {
                "name": nak_name,
                "pada": nak_pada,
                "lord": nak_lord,
                "display": f"{nak_name} (Pada {nak_pada}) — Lord: {nak_lord}",
            },
            "yoga": {
                "name": yoga_name,
                "quality": yoga_quality,
                "display": f"{yoga_name} ({yoga_quality})",
            },
            "karana": {"name": karana_name, "display": karana_name},
            "vara": {
                "name": vara_name,
                "hindi": vara_hindi,
                "lord": vara_lord,
                "display": f"{vara_name} ({vara_hindi}) — Lord: {vara_lord}",
            },
        },
        "inauspicious": {
            "rahu_kaal": rahu_kaal,
            "yamgandam": yamgandam,
            "gulikai": gulikai,
        },
        "abhijit_muhurat": abhijit,
        "choghadiya": {
            "day": day_cho,
            "night": night_cho,
        },
    }
