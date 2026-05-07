import logging
import os
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

from interpretation_engine import generate_interpretation_report
from chart_generator import generate_kundli_chart
from pdf_report import build_kundli_pdf
from panchang_engine import calculate_panchang

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import BackgroundTasks
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from kundli_engine import BirthData, KundliEngine

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="DharmaPath Kundli Web App",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from timezonefinder import TimezoneFinder
_tf = TimezoneFinder()


class KundliRequest(BaseModel):
    birth_date: str
    birth_time: str
    timezone_offset_hours: float
    latitude: float
    longitude: float
    place: str = ""

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lng(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("timezone_offset_hours")
    @classmethod
    def validate_tz(cls, v):
        if not (-14 <= v <= 14):
            raise ValueError("Timezone offset must be between -14 and 14")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_date(cls, v):
        try:
            parsed = datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        if parsed.date() > datetime.today().date():
            raise ValueError("Birth date cannot be in the future")
        if parsed.year < 1900:
            raise ValueError("Birth date must be after 1900")
        return v

    @field_validator("birth_time")
    @classmethod
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM")
        return v

    @field_validator("place")
    @classmethod
    def validate_place(cls, v):
        if len(v) > 200:
            raise ValueError("Place name is too long")
        return v


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: https://www.astrojyotisha.com/sitemap.xml\n"
    )


@app.get("/sitemap.xml")
async def sitemap():
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        "<url>"
        "<loc>https://www.astrojyotisha.com/</loc>"
        "<changefreq>monthly</changefreq>"
        "<priority>1.0</priority>"
        "</url>"
        "</urlset>"
    )
    return HTMLResponse(content=content, media_type="application/xml")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"today": datetime.today().strftime("%Y-%m-%d")},
    )


@app.get("/api/location-search")
@limiter.limit("30/minute")
async def location_search(request: Request, q: str):
    if not q or len(q.strip()) < 2:
        return {"results": []}

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": q,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    headers = {"User-Agent": "DharmaPathKundli/1.0 seva@dharmpathusa.com"}

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params, headers=headers)

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Location service failed")

    items = r.json()
    if not items:
        return {"results": []}

    item = items[0]
    lat = float(item["lat"])
    lng = float(item["lon"])
    address = item.get("address", {})

    city = address.get("city") or address.get("town") or address.get("village") or address.get("county") or ""
    state = address.get("state", "")
    country = address.get("country", "")
    display = ", ".join(x for x in [city, state, country] if x) or item.get("display_name", "")

    timezone_id = _tf.timezone_at(lng=lng, lat=lat)
    gmt_offset = None
    if timezone_id:
        tz = ZoneInfo(timezone_id)
        offset_seconds = datetime.now(tz).utcoffset().total_seconds()
        gmt_offset = round(offset_seconds / 3600, 2)

    return {"results": [{
        "name": city,
        "countryName": country,
        "adminName1": state,
        "lat": lat,
        "lng": lng,
        "timezoneId": timezone_id,
        "gmtOffset": gmt_offset,
        "display": display,
    }]}


@app.post("/api/generate-kundli")
@limiter.limit("15/minute")
async def generate_kundli(request: Request, payload: KundliRequest):
    try:
        birth_dt = f"{payload.birth_date} {payload.birth_time}:00"
        birth_data = BirthData(
            birth_datetime_local=birth_dt,
            timezone_offset_hours=payload.timezone_offset_hours,
            latitude=payload.latitude,
            longitude=payload.longitude,
            place=payload.place,
        )
        engine = KundliEngine(birth_data)
        result = engine.calculate_all()
        return JSONResponse(result)

    except Exception as exc:
        logger.exception("Error in generate_kundli")
        raise HTTPException(status_code=400, detail="Invalid birth data. Please check all fields and try again.")


@app.post("/generate-file")
@limiter.limit("5/minute")
async def generate_file(request: Request, payload: KundliRequest, background_tasks: BackgroundTasks):
    try:
        birth_dt = f"{payload.birth_date} {payload.birth_time}:00"
        birth_data = BirthData(
            birth_datetime_local=birth_dt,
            timezone_offset_hours=payload.timezone_offset_hours,
            latitude=payload.latitude,
            longitude=payload.longitude,
            place=payload.place,
        )

        engine = KundliEngine(birth_data)
        result = engine.calculate_all()
        interpretation_sections = generate_interpretation_report(result)

        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False, dir="/tmp",
            prefix=f"kundli_{payload.birth_date}_"
        ) as f:
            path = f.name

        build_kundli_pdf(result, interpretation_sections, path)
        filename = f"kundli_{payload.birth_date}.pdf"
        background_tasks.add_task(os.unlink, path)

        return FileResponse(
            path,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.exception("Error in generate_file")
        raise HTTPException(status_code=400, detail="Failed to generate PDF. Please check all fields and try again.")


# ── Panchang ─────────────────────────────────────────────────────────────────

class PanchangRequest(BaseModel):
    date: str
    latitude: float
    longitude: float
    timezone_offset_hours: float
    place: str = ""

    @field_validator("latitude")
    @classmethod
    def val_lat(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def val_lng(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("timezone_offset_hours")
    @classmethod
    def val_tz(cls, v):
        if not (-14 <= v <= 14):
            raise ValueError("Timezone offset must be between -14 and 14")
        return v

    @field_validator("date")
    @classmethod
    def val_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date. Use YYYY-MM-DD")
        return v


@app.get("/panchang", response_class=HTMLResponse)
async def panchang_page(request: Request):
    return templates.TemplateResponse(
        request,
        "panchang.html",
        {"today": datetime.today().strftime("%Y-%m-%d")},
    )


@app.post("/api/panchang")
@limiter.limit("30/minute")
async def panchang_api(request: Request, payload: PanchangRequest):
    try:
        result = calculate_panchang(
            date_str=payload.date,
            lat=payload.latitude,
            lng=payload.longitude,
            tz_offset=payload.timezone_offset_hours,
            place=payload.place,
        )
        return result
    except Exception as exc:
        logger.exception("Error in panchang_api")
        raise HTTPException(status_code=400, detail=str(exc))
