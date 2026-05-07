from __future__ import annotations

import calendar as _cal
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


def _calc_planets(jd: float, flags: int) -> Tuple[float, float]:
    """Return (sun_lon, moon_lon) at given JD."""
    try:
        s, _ = swe.calc_ut(jd, swe.SUN, flags)
        m, _ = swe.calc_ut(jd, swe.MOON, flags)
    except Exception:
        fb = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
        s, _ = swe.calc_ut(jd, swe.SUN, fb)
        m, _ = swe.calc_ut(jd, swe.MOON, fb)
    return s[0] % 360, m[0] % 360


def _tithi_idx(sun_lon: float, moon_lon: float) -> int:
    return int((moon_lon - sun_lon) % 360 / 12)


def _find_tithi_end(idx_at_start: int, jd_start: float, jd_limit: float, flags: int) -> float | None:
    """Binary search for the JD when tithi index changes. Returns None if no change before jd_limit."""
    s, m = _calc_planets(jd_limit, flags)
    if _tithi_idx(s, m) == idx_at_start:
        return None  # Tithi does not change before the limit
    lo, hi = jd_start, jd_limit
    for _ in range(50):  # 50 iterations → ~sub-second precision
        mid = (lo + hi) / 2
        s, m = _calc_planets(mid, flags)
        if _tithi_idx(s, m) == idx_at_start:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _nak_idx(moon_lon: float) -> int:
    return int(moon_lon / (360 / 27))


def _find_nak_end(idx_at_start: int, jd_start: float, jd_limit: float, flags: int) -> float | None:
    """Binary search for the JD when nakshatra index changes."""
    _, m = _calc_planets(jd_limit, flags)
    if _nak_idx(m) == idx_at_start:
        return None
    lo, hi = jd_start, jd_limit
    for _ in range(50):
        mid = (lo + hi) / 2
        _, m = _calc_planets(mid, flags)
        if _nak_idx(m) == idx_at_start:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _karana_idx(sun_lon: float, moon_lon: float) -> int:
    return int((moon_lon - sun_lon) % 360 / 6)  # 0–59


def _karana_name(k_idx: int) -> str:
    if k_idx == 0:
        return "Kimstughna"
    elif 1 <= k_idx <= 56:
        return MOVABLE_KARANAS[(k_idx - 1) % 7]
    elif k_idx == 57:
        return "Shakuni"
    elif k_idx == 58:
        return "Chatushpada"
    else:
        return "Naga"


def _find_karana_end(idx_at_start: int, jd_start: float, jd_limit: float, flags: int) -> float | None:
    s, m = _calc_planets(jd_limit, flags)
    if _karana_idx(s, m) == idx_at_start:
        return None
    lo, hi = jd_start, jd_limit
    for _ in range(50):
        mid = (lo + hi) / 2
        s, m = _calc_planets(mid, flags)
        if _karana_idx(s, m) == idx_at_start:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


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
    # Local noon → UTC for sunrise search anchor
    local_noon = date.replace(hour=12, minute=0, second=0)
    utc_noon = local_noon - timedelta(hours=tz_offset)
    jd = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day,
                    utc_noon.hour + utc_noon.minute / 60.0, swe.GREG_CAL)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # ── Vara (weekday based on calendar date, not sunrise) ────────────────────
    py_wd = date.weekday()   # 0=Mon
    sun_wd = (py_wd + 1) % 7  # 0=Sun
    vara_name  = VARAS[sun_wd]
    vara_hindi = VARA_HINDI[sun_wd]
    vara_lord  = VARA_LORDS[sun_wd]

    # ── Sunrise / Sunset / Next Sunrise ──────────────────────────────────────
    geopos    = (lng, lat, 0.0)
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

    try:
        _, tret_rise_next = swe.rise_trans(jd_sunset, swe.SUN, rsmi_rise, geopos, 0, 0, swe.FLG_SWIEPH)
        jd_next_sunrise = tret_rise_next[0]
    except Exception:
        jd_next_sunrise = jd_sunrise + 1.0

    # ── Planets at Sunrise (authentic Panchang reference point) ──────────────
    sun_lon, moon_lon = _calc_planets(jd_sunrise, flags)

    # ── Tithi — with intra-day transition ────────────────────────────────────
    t_idx = _tithi_idx(sun_lon, moon_lon)
    tithi_end_jd = _find_tithi_end(t_idx, jd_sunrise, jd_next_sunrise, flags)

    def _tithi_entry(idx: int) -> Dict:
        return {
            "number": (idx % 15) + 1,
            "name": TITHIS[idx],
            "paksha": TITHI_PAKSHA[idx],
        }

    if tithi_end_jd is None:
        tithis = [_tithi_entry(t_idx)]  # Single tithi prevails all day
    else:
        end_str = _jd_to_local_time(tithi_end_jd, tz_offset)
        t2_idx  = (t_idx + 1) % 30
        t1 = {**_tithi_entry(t_idx),  "upto": end_str}
        t2 = {**_tithi_entry(t2_idx), "from": end_str}
        tithis = [t1, t2]

    # ── Nakshatra — with intra-day transition ─────────────────────────────────
    n_idx = _nak_idx(moon_lon)
    nak_end_jd = _find_nak_end(n_idx, jd_sunrise, jd_next_sunrise, flags)

    def _nak_entry(idx: int, moon_l: float) -> Dict:
        return {
            "name": NAKSHATRAS[idx],
            "pada": int((moon_l % (360 / 27)) / (360 / 108)) + 1,
            "lord": NAKSHATRA_LORDS[idx],
        }

    if nak_end_jd is None:
        nakshatras = [_nak_entry(n_idx, moon_lon)]
    else:
        nak_end_str = _jd_to_local_time(nak_end_jd, tz_offset)
        n2_idx = (n_idx + 1) % 27
        _, m2_lon = _calc_planets(nak_end_jd + 1 / 1440, flags)  # 1 min after end
        n1 = {**_nak_entry(n_idx, moon_lon), "upto": nak_end_str}
        n2 = {**_nak_entry(n2_idx, m2_lon),  "from": nak_end_str}
        nakshatras = [n1, n2]

    # ── Yoga ─────────────────────────────────────────────────────────────────
    yoga_idx     = int(((sun_lon + moon_lon) % 360) / (360 / 27))
    yoga_name    = YOGAS[yoga_idx]
    yoga_quality = YOGA_QUALITY.get(yoga_name, "neutral")

    # ── Karana — collect all transitions between sunrise and next sunrise ────
    # ~12° Moon-Sun movement per day → typically 2 Karana changes per day
    karanas: List[Dict] = []
    k_jd = jd_sunrise
    k_sun, k_moon = sun_lon, moon_lon
    for _ in range(5):  # safety cap — max ~3 Karanas per day
        k_idx = _karana_idx(k_sun, k_moon)
        k_end_jd = _find_karana_end(k_idx, k_jd, jd_next_sunrise, flags)
        entry: Dict = {"name": _karana_name(k_idx)}
        if karanas:
            entry["from"] = _jd_to_local_time(k_jd, tz_offset)
        if k_end_jd is None:
            karanas.append(entry)
            break
        entry["upto"] = _jd_to_local_time(k_end_jd, tz_offset)
        karanas.append(entry)
        k_jd = k_end_jd
        k_sun, k_moon = _calc_planets(k_jd + 1 / 1440, flags)  # 1 min past end

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
            "tithis": tithis,         # list: 1 entry (all-day) or 2 entries (with transition time)
            "nakshatras": nakshatras, # list: 1 entry or 2 entries
            "yoga": {
                "name": yoga_name,
                "quality": yoga_quality,
            },
            "karanas": karanas,  # list: 1–3 entries with optional from/upto times
            "vara": {
                "name": vara_name,
                "hindi": vara_hindi,
                "lord": vara_lord,
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


def calculate_month_panchang(
    year: int,
    month: int,
    lat: float,
    lng: float,
    tz_offset: float,
) -> List[Dict]:
    """Return Tithi data for every day of a calendar month (lean, no Choghadiya)."""
    if EPHE_DIR.exists():
        swe.set_ephe_path(str(EPHE_DIR))
    else:
        swe.set_ephe_path(str(BASE_DIR))
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    flags     = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    geopos    = (lng, lat, 0.0)
    rsmi_rise = swe.CALC_RISE | swe.BIT_DISC_CENTER
    rsmi_set  = swe.CALC_SET  | swe.BIT_DISC_CENTER

    num_days = _cal.monthrange(year, month)[1]
    result: List[Dict] = []

    for day in range(1, num_days + 1):
        date     = datetime(year, month, day)
        date_str = date.strftime("%Y-%m-%d")

        utc_noon = date.replace(hour=12) - timedelta(hours=tz_offset)
        jd = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day,
                        utc_noon.hour + utc_noon.minute / 60.0, swe.GREG_CAL)

        try:
            _, tret = swe.rise_trans(jd - 0.5, swe.SUN, rsmi_rise, geopos, 0, 0, swe.FLG_SWIEPH)
            jd_sunrise = tret[0]
        except Exception:
            jd_sunrise = jd - 0.25

        try:
            _, tret = swe.rise_trans(jd_sunrise, swe.SUN, rsmi_set, geopos, 0, 0, swe.FLG_SWIEPH)
            jd_sunset = tret[0]
        except Exception:
            jd_sunset = jd + 0.25

        try:
            _, tret = swe.rise_trans(jd_sunset, swe.SUN, rsmi_rise, geopos, 0, 0, swe.FLG_SWIEPH)
            jd_next_sunrise = tret[0]
        except Exception:
            jd_next_sunrise = jd_sunrise + 1.0

        sun_lon, moon_lon = _calc_planets(jd_sunrise, flags)
        t_idx         = _tithi_idx(sun_lon, moon_lon)
        tithi_end_jd  = _find_tithi_end(t_idx, jd_sunrise, jd_next_sunrise, flags)

        def _entry(idx: int) -> Dict:
            return {
                "number": (idx % 15) + 1,
                "name":   TITHIS[idx],
                "paksha": TITHI_PAKSHA[idx],
            }

        if tithi_end_jd is None:
            tithis = [_entry(t_idx)]
        else:
            end_str = _jd_to_local_time(tithi_end_jd, tz_offset)
            t2_idx  = (t_idx + 1) % 30
            tithis  = [
                {**_entry(t_idx),  "upto": end_str},
                {**_entry(t2_idx), "from": end_str},
            ]

        py_wd  = date.weekday()
        sun_wd = (py_wd + 1) % 7  # 0 = Sunday

        result.append({
            "date":    date_str,
            "day":     day,
            "weekday": sun_wd,
            "tithis":  tithis,
        })

    return result
