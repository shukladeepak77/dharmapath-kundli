import logging
import os
import tempfile
from datetime import datetime

from interpretation_engine import generate_interpretation_report
from chart_generator import generate_kundli_chart
from pdf_report import build_kundli_pdf

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
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

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "demo")


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
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
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


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"geonames_username": GEONAMES_USERNAME},
    )


@app.get("/api/location-search")
@limiter.limit("30/minute")
async def location_search(request: Request, q: str):
    if not q or len(q.strip()) < 2:
        return {"results": []}

    url = "http://api.geonames.org/searchJSON"
    params = {
        "q": q,
        "maxRows": 1,
        "username": GEONAMES_USERNAME,
        "style": "FULL",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Location service failed")

    data = r.json()
    results = []
    for item in data.get("geonames", []):
        timezone_info = item.get("timezone") or {}
        results.append({
            "name": item.get("name"),
            "countryName": item.get("countryName"),
            "adminName1": item.get("adminName1"),
            "lat": float(item.get("lat")),
            "lng": float(item.get("lng")),
            "timezoneId": timezone_info.get("timeZoneId"),
            "gmtOffset": timezone_info.get("gmtOffset"),
            "display": ", ".join(
                x for x in [item.get("name"), item.get("adminName1"), item.get("countryName")] if x
            ),
        })

    return {"results": results}


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
