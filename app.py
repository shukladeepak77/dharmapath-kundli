import os
import json
from pdf_chart import draw_north_indian_chart
from interpretation_engine import generate_interpretation_report
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from typing import Optional
from chart_generator import generate_kundli_chart

import httpx
from fastapi import FastAPI, Form, HTTPException, Request
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
            name=payload.get("name", "Native"),
            gender=payload.get("gender", ""),
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
async def generate_file(
    name: str = Form(...),
    gender: str = Form(""),
    birth_date: str = Form(...),
    birth_time: str = Form(...),
    place: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timezone_offset_hours: float = Form(...),
):
    birth_data = BirthData(
        name=name,
        gender=gender,
        birth_datetime_local=f"{birth_date} {birth_time}:00",
        timezone_offset_hours=timezone_offset_hours,
        latitude=latitude,
        longitude=longitude,
        place=place,
    )

    engine = KundliEngine(birth_data)
    result = engine.calculate_all()
    chart_path = generate_kundli_chart(result["d1_rashi_chart"])
    interpretation_sections = generate_interpretation_report(result)

    safe_name = "".join(c for c in name if c.isalnum() or c in ["_", "-"]).strip() or "native"
    filename = f"kundli_{safe_name}.pdf"
    path = os.path.join("/tmp", filename)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 40, "DharmaPath Janam Kundli Report")
    chart_size = 340
    chart_x = (width - chart_size) / 2
    chart_y = height - 420

    draw_north_indian_chart(
        c,
        result["d1_chart_visual"],
        chart_x,
        chart_y,
        chart_size,
        "D1 Rashi Chart"
    )

    y = chart_y - 50

    def title(text, y):
        c.setFillColor(colors.HexColor("#7c2d12"))
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, text)
        c.setFillColor(colors.black)

    def line(text, y, size=10):
        c.setFont("Helvetica", size)
        c.drawString(50, y, text)

    def section(text, y):
        c.setFillColor(colors.HexColor("#9a3412"))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, text)
        c.setFillColor(colors.black)

    def paragraph(text, y, size=9, max_chars=95):
        c.setFont("Helvetica", size)
        words = text.split()
        current = ""

        for word in words:
            if len(current + " " + word) <= max_chars:
                current += " " + word if current else word
            else:
                c.drawString(50, y, current)
                y -= 13
                current = word

                if y < 60:
                    c.showPage()
                    y = height - 50

        if current:
            c.drawString(50, y, current)
            y -= 15

        return y

    #y = height - 50

    #title("DharmaPath Janam Kundli Report", y)
    #y -= 35

    section("Birth Details", y)
    y -= 20
    line(f"Name: {name}", y); y -= 15
    line(f"Gender: {gender}", y); y -= 15
    line(f"Birth Date/Time: {birth_date} {birth_time}", y); y -= 15
    line(f"Place: {place}", y); y -= 15
    line(f"Latitude: {latitude}, Longitude: {longitude}", y); y -= 15
    line(f"Timezone Offset: UTC{timezone_offset_hours:+}", y); y -= 15
    line(f"Lahiri Ayanamsha: {result['ayanamsha_lahiri']}", y); y -= 30

    section("D1 Rashi Chart - Planetary Positions", y)
    y -= 20

    d1 = result["d1_rashi_chart"]
    order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "Planet")
    c.drawString(120, y, "Rashi")
    c.drawString(220, y, "Degree")
    c.drawString(290, y, "House")
    c.drawString(350, y, "Nakshatra")
    c.drawString(470, y, "Pada")
    y -= 14

    c.setFont("Helvetica", 9)
    for p in order:
        x = d1[p]
        c.drawString(50, y, p)
        c.drawString(120, y, x["rashi"])
        c.drawString(220, y, str(round(x["degree_in_rashi"], 2)))
        c.drawString(290, y, str(x["house"]))
        c.drawString(350, y, x["nakshatra"])
        c.drawString(470, y, str(x["pada"]))
        y -= 14

    y -= 20
    section("D9 Navamsa Chart - Planetary Positions", y)
    y -= 20

    d9 = result["d9_navamsa_chart"]

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "Planet")
    c.drawString(120, y, "Rashi")
    c.drawString(220, y, "Degree")
    c.drawString(290, y, "House")
    c.drawString(350, y, "Nakshatra")
    c.drawString(470, y, "Pada")
    y -= 14

    c.setFont("Helvetica", 9)
    for p in order:
        x = d9[p]
        c.drawString(50, y, p)
        c.drawString(120, y, x["rashi"])
        c.drawString(220, y, str(round(x["degree_in_rashi"], 2)))
        c.drawString(290, y, str(x["house"]))
        c.drawString(350, y, x["nakshatra"])
        c.drawString(470, y, str(x["pada"]))
        y -= 14

    c.showPage()
    y = height - 50

    title("Vimshottari Mahadasha", y)
    y -= 35

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Lord")
    c.drawString(150, y, "Start")
    c.drawString(260, y, "End")
    c.drawString(370, y, "Years")
    y -= 18

    c.setFont("Helvetica", 10)
    for d in result["vimshottari_mahadasha"]:
        c.drawString(50, y, d["lord"])
        c.drawString(150, y, d["start"])
        c.drawString(260, y, d["end"])
        c.drawString(370, y, str(d["years"]))
        y -= 18

    y -= 30
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.gray)
    c.drawString(50, y, "Generated by DharmaPath Kundli Engine using Swiss Ephemeris calculations.")

    c.showPage()
    y = height - 50

    title("Detailed Kundli Interpretation", y)
    y -= 35

    for item in interpretation_sections:
        if y < 100:
            c.showPage()
            y = height - 50

        section(item["title"], y)
        y -= 20

        for para in item["paragraphs"]:
            y = paragraph(para, y)

        y -= 10
    
    c.save()

    return FileResponse(path, media_type="application/pdf", filename=filename)

