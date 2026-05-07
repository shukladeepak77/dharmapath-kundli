from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from panchang_engine import calculate_panchang

# ── Event rule definitions ────────────────────────────────────────────────────

EVENT_RULES: Dict[str, Dict] = {
    "vivah": {
        "label": "Vivah — Wedding",
        "tithi_good":  {("Shukla", n) for n in [2, 3, 5, 7, 10, 11, 13]},
        "tithi_bad":   {("Shukla", n) for n in [4, 6, 8, 9, 12, 14, 15]}
                     | {("Krishna", n) for n in range(1, 16)},
        "nakshatra_good": {"Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta",
                           "Swati", "Anuradha", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"},
        "nakshatra_bad":  {"Bharani", "Krittika", "Ardra", "Ashlesha", "Jyeshtha", "Mula",
                           "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"},
        "vara_good": {1, 3, 4, 5},   # Mon, Wed, Thu, Fri
        "vara_bad":  {0, 2, 6},      # Sun, Tue, Sat
    },
    "griha_pravesh": {
        "label": "Griha Pravesh — Housewarming",
        "tithi_good":  {("Shukla", n) for n in [2, 3, 5, 7, 10, 11, 13]},
        "tithi_bad":   {("Shukla", n) for n in [4, 6, 8, 9, 12, 14]}
                     | {("Krishna", n) for n in range(1, 16)},
        "nakshatra_good": {"Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                           "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada",
                           "Revati", "Dhanishtha", "Shravana"},
        "nakshatra_bad":  {"Bharani", "Krittika", "Ardra", "Ashlesha", "Jyeshtha",
                           "Mula", "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"},
        "vara_good": {3, 4, 5},      # Wed, Thu, Fri
        "vara_bad":  {0, 2, 6},      # Sun, Tue, Sat
    },
    "vyapar": {
        "label": "Vyapar Arambha — Business Start",
        "tithi_good":  {("Shukla", n) for n in [1, 2, 3, 5, 6, 7, 10, 11, 12, 13]},
        "tithi_bad":   {("Shukla", n) for n in [4, 8, 9, 14]}
                     | {("Krishna", n) for n in [8, 9, 14, 15]},
        "nakshatra_good": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                           "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
                           "Dhanishtha", "Shatabhisha", "Revati"},
        "nakshatra_bad":  {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula",
                           "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"},
        "vara_good": {1, 3, 4, 5},
        "vara_bad":  {6},            # Sat
    },
    "naamkaran": {
        "label": "Naamkaran — Naming Ceremony",
        "tithi_good":  {("Shukla", n) for n in [2, 3, 5, 7, 10, 11, 13]},
        "tithi_bad":   {("Shukla", 14), ("Krishna", 14), ("Krishna", 15)},
        "nakshatra_good": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                           "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
                           "Dhanishtha", "Uttara Phalguni", "Uttara Ashadha",
                           "Uttara Bhadrapada", "Revati"},
        "nakshatra_bad":  {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula",
                           "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"},
        "vara_good": {1, 3, 4, 5},
        "vara_bad":  {0, 2, 6},
    },
    "yatra": {
        "label": "Yatra — Travel",
        "tithi_good":  {("Shukla", n) for n in [2, 3, 5, 6, 7, 10, 11, 12, 13]}
                     | {("Krishna", n) for n in [2, 3, 5, 6, 7]},
        "tithi_bad":   {("Shukla", 14), ("Shukla", 15), ("Krishna", 14), ("Krishna", 15)},
        "nakshatra_good": {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                           "Anuradha", "Shravana", "Revati", "Swati"},
        "nakshatra_bad":  {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula",
                           "Purva Phalguni", "Purva Ashadha", "Purva Bhadrapada"},
        "vara_good": {1, 3, 4, 5},
        "vara_bad":  {2, 6},         # Tue, Sat
    },
    "mundan": {
        "label": "Mundan — First Haircut",
        "tithi_good":  {("Shukla", n) for n in [2, 3, 5, 6, 7, 10, 11, 12, 13]},
        "tithi_bad":   {("Shukla", 14), ("Shukla", 15), ("Krishna", 14), ("Krishna", 15)},
        "nakshatra_good": {"Mrigashira", "Punarvasu", "Hasta", "Chitra", "Swati",
                           "Jyeshtha", "Shravana", "Dhanishtha", "Revati"},
        "nakshatra_bad":  {"Bharani", "Ardra", "Ashlesha", "Mula", "Purva Phalguni",
                           "Purva Ashadha", "Purva Bhadrapada"},
        "vara_good": {1, 3, 4, 5},
        "vara_bad":  {0, 2, 6},
    },
}

_VARA_IDX = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3,
             "Thursday": 4, "Friday": 5, "Saturday": 6}


def _time_to_min(t: str) -> int:
    """Convert '09:15 AM' / '01:30 PM' to minutes since midnight."""
    dt = datetime.strptime(t, "%I:%M %p")
    return dt.hour * 60 + dt.minute


def _overlaps(s1: str, e1: str, s2: str, e2: str) -> bool:
    return _time_to_min(s1) < _time_to_min(e2) and _time_to_min(e1) > _time_to_min(s2)


def _best_windows(panchang_data: Dict) -> List[Dict]:
    """Return Choghadiya slots with quality excellent/good that don't clash with inauspicious periods."""
    ina = panchang_data["inauspicious"]
    bad_periods = [ina["rahu_kaal"], ina["yamgandam"], ina["gulikai"]]
    good_qualities = {"excellent", "good"}
    windows = []
    all_slots = panchang_data["choghadiya"]["day"] + panchang_data["choghadiya"]["night"]
    for slot in all_slots:
        if slot["quality"] not in good_qualities:
            continue
        clashes = any(_overlaps(slot["start"], slot["end"], p["start"], p["end"])
                      for p in bad_periods)
        if not clashes:
            windows.append({"name": slot["name"], "start": slot["start"], "end": slot["end"]})
    return windows[:4]


def find_muhurat(
    start_date: str,
    end_date: str,
    lat: float,
    lng: float,
    tz_offset: float,
    event_type: str,
    place: str = "",
) -> Dict:
    if event_type not in EVENT_RULES:
        raise ValueError(f"Unknown event type: {event_type}")

    rules = EVENT_RULES[event_type]
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end   = datetime.strptime(end_date,   "%Y-%m-%d")

    results: List[Dict] = []
    current = start

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        try:
            pd = calculate_panchang(date_str, lat, lng, tz_offset, place)
        except Exception:
            current += timedelta(days=1)
            continue

        p   = pd["panchang"]
        t   = p["tithis"][0]
        n   = p["nakshatras"][0]
        vara = p["vara"]
        yoga = p["yoga"]

        # ── Score Tithi ───────────────────────────────────────────────────────
        tkey = (t["paksha"], t["number"])
        if tkey in rules["tithi_good"]:
            t_score, t_qual = 3, "good"
        elif tkey in rules["tithi_bad"]:
            t_score, t_qual = 0, "inauspicious"
        else:
            t_score, t_qual = 1, "neutral"

        # ── Score Nakshatra ───────────────────────────────────────────────────
        nname = n["name"]
        if nname in rules["nakshatra_good"]:
            n_score, n_qual = 3, "good"
        elif nname in rules["nakshatra_bad"]:
            n_score, n_qual = 0, "inauspicious"
        else:
            n_score, n_qual = 1, "neutral"

        # ── Score Vara ────────────────────────────────────────────────────────
        vidx = _VARA_IDX.get(vara["name"], -1)
        if vidx in rules["vara_good"]:
            v_score, v_qual = 2, "good"
        elif vidx in rules["vara_bad"]:
            v_score, v_qual = 0, "inauspicious"
        else:
            v_score, v_qual = 1, "neutral"

        # Yoga: +1 auspicious, 0 neutral, -1 inauspicious
        if yoga["quality"] in ("auspicious", "excellent"):
            yoga_score = 1
        elif yoga["quality"] == "inauspicious":
            yoga_score = -1
        else:
            yoga_score = 0

        total = t_score + n_score + v_score + yoga_score

        # Skip days where both Tithi and Nakshatra are inauspicious
        if t_score == 0 and n_score == 0:
            current += timedelta(days=1)
            continue

        if total < 4:
            current += timedelta(days=1)
            continue

        rating = "Excellent" if total >= 8 else ("Good" if total >= 6 else "Acceptable")

        results.append({
            "date":    date_str,
            "score":   total,
            "rating":  rating,
            "sunrise": pd["sunrise"],
            "tithi":    {"name": t["name"], "paksha": t["paksha"],
                         "number": t["number"], "quality": t_qual},
            "nakshatra": {"name": nname, "pada": n["pada"], "quality": n_qual},
            "vara":      {"name": vara["name"], "hindi": vara["hindi"], "quality": v_qual},
            "yoga":      {"name": yoga["name"], "quality": yoga["quality"], "score": yoga_score},
            "rahu_kaal": pd["inauspicious"]["rahu_kaal"],
            "windows":   _best_windows(pd),
        })

        current += timedelta(days=1)

    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "event_type":  event_type,
        "event_label": rules["label"],
        "start_date":  start_date,
        "end_date":    end_date,
        "place":       place,
        "total_found": len(results),
        "results":     results,
    }
