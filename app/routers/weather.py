import csv
import io
import math
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.database import get_db
from app.schemas import PaginatedHistory, WeatherData, WeatherQueryResponse
from app.services.weather import fetch_weather

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api", tags=["weather"])


def convert_units(cached: WeatherData, target_unit: str) -> WeatherData:
    """Convert weather data from metric to imperial or vice versa."""
    if cached.unit == target_unit:
        return cached

    if target_unit == "imperial":
        temperature = cached.temperature * 9 / 5 + 32
        feels_like = cached.feels_like * 9 / 5 + 32
        wind_speed = round(cached.wind_speed * 2.237, 2)
    else:
        temperature = (cached.temperature - 32) * 5 / 9
        feels_like = (cached.feels_like - 32) * 5 / 9
        wind_speed = round(cached.wind_speed / 2.237, 2)

    return WeatherData(
        city=cached.city,
        temperature=round(temperature, 1),
        feels_like=round(feels_like, 1),
        description=cached.description,
        humidity=cached.humidity,
        wind_speed=wind_speed,
        unit=target_unit,
    )


@router.get("/weather", response_model=WeatherQueryResponse)
@limiter.limit(settings.rate_limit)
async def get_weather(
    request: Request,
    city: str = Query(min_length=1, max_length=100),
    unit: Literal["metric", "imperial"] = Query("metric"),
    db: Session = Depends(get_db),
):
    city = city.strip()
    cached = crud.get_recent_query(db, city)
    if cached:
        cached_data = WeatherData(
            city=cached.city,
            temperature=cached.temperature,
            feels_like=cached.feels_like,
            description=cached.description,
            humidity=cached.humidity,
            wind_speed=cached.wind_speed,
            unit=cached.unit,
        )
        weather_data = convert_units(cached_data, unit)
        return crud.save_query(db, weather_data, from_cache=True)

    weather_data = await fetch_weather(city, unit)
    return crud.save_query(db, weather_data, from_cache=False)


@router.get("/history", response_model=PaginatedHistory)
def get_history(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    city: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
):
    items, total = crud.get_history(
        db,
        page=page,
        page_size=page_size,
        city=city,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedHistory(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/history/export")
def export_history(
    db: Session = Depends(get_db),
    city: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
):
    rows = crud.get_all_history(
        db, city=city, date_from=date_from, date_to=date_to
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "city", "temperature", "feels_like", "description",
        "humidity", "wind_speed", "unit", "from_cache", "queried_at",
    ])
    for r in rows:
        writer.writerow([
            r.id, r.city, r.temperature, r.feels_like, r.description,
            r.humidity, r.wind_speed, r.unit, r.from_cache, r.queried_at,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=weather_history.csv"
        },
    )


@router.delete("/history/{query_id}", status_code=204)
def delete_history_entry(query_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_query(db, query_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found.")
