from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import swisseph as swe

BASE_DIR = Path(__file__).resolve().parent
EPHE_DIR = BASE_DIR / "ephe"

RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

PLANET_SHORT = {
    "Lagna": "La", "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
}

VIMSHOTTARI_SEQUENCE = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
] * 3


@dataclass(frozen=True)
class BirthData:
    name: str
    gender: str
    birth_datetime_local: str
    timezone_offset_hours: float
    latitude: float
    longitude: float
    place: str = ""


@dataclass(frozen=True)
class PlanetPosition:
    planet: str
    short: str
    longitude: float
    rashi_index: int
    rashi_number: int
    rashi: str
    degree_in_rashi: float
    nakshatra_index: int
    nakshatra: str
    pada: int
    house: int
    speed: float
    retrograde: bool


@dataclass(frozen=True)
class DashaPeriod:
    lord: str
    start: str
    end: str
    years: float


def normalize_deg(value: float) -> float:
    return value % 360.0


def parse_local_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def local_to_utc(local_dt: datetime, timezone_offset_hours: float) -> datetime:
    return local_dt - timedelta(hours=timezone_offset_hours)


def decimal_hour(dt: datetime) -> float:
    return dt.hour + dt.minute / 60.0 + dt.second / 3600.0 + dt.microsecond / 3_600_000_000.0


def get_rashi(longitude: float) -> Tuple[int, int, str, float]:
    longitude = normalize_deg(longitude)
    rashi_index = int(longitude // 30)
    rashi_number = rashi_index + 1
    degree_in_rashi = longitude % 30
    return rashi_index, rashi_number, RASHIS[rashi_index], degree_in_rashi


def get_nakshatra(longitude: float) -> Tuple[int, str, int]:
    longitude = normalize_deg(longitude)
    nak_len = 360.0 / 27.0
    pada_len = nak_len / 4.0
    nak_index = int(longitude // nak_len)
    pada = int((longitude % nak_len) // pada_len) + 1
    return nak_index, NAKSHATRAS[nak_index], pada


def navamsa_longitude(d1_longitude: float) -> float:
    lon = normalize_deg(d1_longitude)
    sign = int(lon // 30)
    deg_in_sign = lon % 30
    nav_part = int(deg_in_sign // (30.0 / 9.0))

    if sign in [0, 3, 6, 9]:
        start_sign = sign
    elif sign in [1, 4, 7, 10]:
        start_sign = (sign + 8) % 12
    else:
        start_sign = (sign + 4) % 12

    nav_sign = (start_sign + nav_part) % 12
    degree_inside_navamsa = (deg_in_sign % (30.0 / 9.0)) * 9.0
    return normalize_deg(nav_sign * 30.0 + degree_inside_navamsa)


def dataclass_dict(obj):
    if isinstance(obj, dict):
        return {k: dataclass_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dataclass_dict(v) for v in obj]
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return obj


class KundliEngine:
    def __init__(self, birth_data: BirthData):
        self.birth_data = birth_data
        self.local_dt = parse_local_datetime(birth_data.birth_datetime_local)
        self.utc_dt = local_to_utc(self.local_dt, birth_data.timezone_offset_hours)

        if EPHE_DIR.exists():
            swe.set_ephe_path(str(EPHE_DIR))
        else:
            swe.set_ephe_path(str(BASE_DIR))

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        self.jd_ut = swe.julday(
            self.utc_dt.year,
            self.utc_dt.month,
            self.utc_dt.day,
            decimal_hour(self.utc_dt),
            swe.GREG_CAL,
        )
        self.ayanamsha = swe.get_ayanamsa_ut(self.jd_ut)

    def calculate_all(self) -> Dict:
        d1 = self.calculate_d1()
        d9 = self.calculate_d9(d1)
        dashas = self.calculate_vimshottari(d1["Moon"])
        chart_data_d1 = self.build_chart_data(d1)
        chart_data_d9 = self.build_chart_data(d9)

        return {
            "birth_data": asdict(self.birth_data),
            "utc_datetime": self.utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "julian_day_ut": round(self.jd_ut, 6),
            "ayanamsha_lahiri": round(self.ayanamsha, 8),
            "d1_rashi_chart": dataclass_dict(d1),
            "d9_navamsa_chart": dataclass_dict(d9),
            "d1_chart_visual": chart_data_d1,
            "d9_chart_visual": chart_data_d9,
            "vimshottari_mahadasha": dataclass_dict(dashas),
        }

    def planet_longitude_sidereal(self, planet_id: int) -> Tuple[float, float]:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        try:
            result, _ = swe.calc_ut(self.jd_ut, planet_id, flags)
        except Exception:
            flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
            result, _ = swe.calc_ut(self.jd_ut, planet_id, flags)

        return normalize_deg(result[0]), result[3]

    def calculate_lagna_sidereal(self) -> float:
        houses, ascmc = swe.houses_ex(
            self.jd_ut,
            self.birth_data.latitude,
            self.birth_data.longitude,
            b"P",
            swe.FLG_SIDEREAL,
        )
        return normalize_deg(ascmc[0])

    def house_from_lagna_sign(self, longitude: float, lagna_longitude: float) -> int:
        lagna_sign = int(lagna_longitude // 30)
        planet_sign = int(longitude // 30)
        return ((planet_sign - lagna_sign) % 12) + 1

    def make_position(self, planet: str, longitude: float, speed: float, lagna_longitude: float) -> PlanetPosition:
        rashi_index, rashi_number, rashi, degree = get_rashi(longitude)
        nak_index, nakshatra, pada = get_nakshatra(longitude)
        house = 1 if planet == "Lagna" else self.house_from_lagna_sign(longitude, lagna_longitude)
        return PlanetPosition(
            planet=planet,
            short=PLANET_SHORT.get(planet, planet[:2]),
            longitude=round(longitude, 8),
            rashi_index=rashi_index,
            rashi_number=rashi_number,
            rashi=rashi,
            degree_in_rashi=round(degree, 8),
            nakshatra_index=nak_index,
            nakshatra=nakshatra,
            pada=pada,
            house=house,
            speed=round(speed, 8),
            retrograde=(speed < 0),
        )

    def calculate_d1(self) -> Dict[str, PlanetPosition]:
        positions: Dict[str, PlanetPosition] = {}
        lagna_lon = self.calculate_lagna_sidereal()
        positions["Lagna"] = self.make_position("Lagna", lagna_lon, 0.0, lagna_lon)

        for planet_name, planet_id in PLANET_IDS.items():
            lon, speed = self.planet_longitude_sidereal(planet_id)
            positions[planet_name] = self.make_position(planet_name, lon, speed, lagna_lon)

        rahu = positions["Rahu"]
        ketu_lon = normalize_deg(rahu.longitude + 180.0)
        positions["Ketu"] = self.make_position("Ketu", ketu_lon, -rahu.speed, lagna_lon)
        return positions

    def calculate_d9(self, d1: Dict[str, PlanetPosition]) -> Dict[str, PlanetPosition]:
        d9: Dict[str, PlanetPosition] = {}
        d9_lagna_lon = navamsa_longitude(d1["Lagna"].longitude)

        for planet, pos in d1.items():
            d9_lon = navamsa_longitude(pos.longitude)
            d9[planet] = self.make_position(planet, d9_lon, pos.speed, d9_lagna_lon)

        return d9

    def calculate_vimshottari(self, moon: PlanetPosition) -> List[DashaPeriod]:
        nak_len = 360.0 / 27.0
        moon_position_inside_nak = moon.longitude % nak_len
        fraction_completed = moon_position_inside_nak / nak_len
        fraction_remaining = 1.0 - fraction_completed

        start_lord = NAKSHATRA_LORDS[moon.nakshatra_index]
        sequence_lords = [lord for lord, _years in VIMSHOTTARI_SEQUENCE]
        start_index = sequence_lords.index(start_lord)

        periods: List[DashaPeriod] = []
        current_start = self.local_dt

        for i in range(9):
            lord, full_years = VIMSHOTTARI_SEQUENCE[(start_index + i) % 9]
            years = full_years * fraction_remaining if i == 0 else full_years
            current_end = current_start + timedelta(days=years * 365.2425)
            periods.append(
                DashaPeriod(
                    lord=lord,
                    start=current_start.strftime("%Y-%m-%d"),
                    end=current_end.strftime("%Y-%m-%d"),
                    years=round(years, 4),
                )
            )
            current_start = current_end
            fraction_remaining = 1.0

        return periods

    def build_chart_data(self, positions: Dict[str, PlanetPosition]) -> Dict:
        lagna_rashi_index = positions["Lagna"].rashi_index
        houses = {}
        for house in range(1, 13):
            rashi_index = (lagna_rashi_index + house - 1) % 12
            houses[str(house)] = {
                "house": house,
                "rashi_number": rashi_index + 1,
                "rashi": RASHIS[rashi_index],
                "planets": [],
            }

        for planet, pos in positions.items():
            label = pos.short + ("R" if pos.retrograde and planet not in ["Lagna", "Rahu", "Ketu"] else "")
            houses[str(pos.house)]["planets"].append({
                "planet": planet,
                "short": label,
                "degree": pos.degree_in_rashi,
                "rashi": pos.rashi,
                "nakshatra": pos.nakshatra,
                "pada": pos.pada,
            })

        return {"houses": houses}
