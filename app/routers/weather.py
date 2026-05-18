import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import PaginatedHistory, WeatherQueryResponse
from app.services.weather import fetch_weather

router = APIRouter(prefix="/api", tags=["weather"])


@router.get("/weather", response_model=WeatherQueryResponse)
async def get_weather(city: str, db: Session = Depends(get_db)):
    weather_data = await fetch_weather(city)
    record = crud.save_query(db, weather_data)
    return record


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


@router.delete("/history/{query_id}", status_code=204)
def delete_history_entry(query_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_query(db, query_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found.")
