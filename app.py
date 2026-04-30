import os
from interpretation_engine import generate_interpretation_report
from chart_generator import generate_kundli_chart
from pdf_report import build_kundli_pdf

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from kundli_engine import BirthData, KundliEngine

app = FastAPI(title="DharmaPath Kundli Web App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "demo")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"geonames_username": GEONAMES_USERNAME},
    )    


@app.get("/api/location-search")
async def location_search(q: str):
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
async def generate_kundli(payload: dict):
    try:
        birth_date = payload["birth_date"]
        birth_time = payload["birth_time"]
        birth_dt = f"{birth_date} {birth_time}:00"

        birth_data = BirthData(
            birth_datetime_local=birth_dt,
            timezone_offset_hours=float(payload["timezone_offset_hours"]),
            latitude=float(payload["latitude"]),
            longitude=float(payload["longitude"]),
            place=payload.get("place", ""),
        )

        engine = KundliEngine(birth_data)
        result = engine.calculate_all()
        chart_path = generate_kundli_chart(result["d1_rashi_chart"])
        return JSONResponse(result)

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))



@app.post("/generate-file")
async def generate_file(payload: dict):
    try:
        birth_date = payload["birth_date"]
        birth_time = payload["birth_time"]
        birth_data = BirthData(
            birth_datetime_local=f"{birth_date} {birth_time}:00",
            timezone_offset_hours=float(payload["timezone_offset_hours"]),
            latitude=float(payload["latitude"]),
            longitude=float(payload["longitude"]),
            place=payload.get("place", ""),
        )

        engine = KundliEngine(birth_data)
        result = engine.calculate_all()
        generate_kundli_chart(result["d1_rashi_chart"])
        interpretation_sections = generate_interpretation_report(result)

        filename = f"kundli_{birth_date}.pdf"
        path = os.path.join("/tmp", filename)
        build_kundli_pdf(result, interpretation_sections, path)

        return FileResponse(
            path,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

