from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import WeatherQueryResponse
from app.services.weather import fetch_weather

router = APIRouter(prefix="/api", tags=["weather"])


@router.get("/weather", response_model=WeatherQueryResponse)
async def get_weather(city: str, db: Session = Depends(get_db)):
    weather_data = await fetch_weather(city)
    record = crud.save_query(db, weather_data)
    return record


@router.get("/history", response_model=list[WeatherQueryResponse])
def get_history(db: Session = Depends(get_db)):
    return crud.get_history(db)


@router.delete("/history/{query_id}", status_code=204)
def delete_history_entry(query_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_query(db, query_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found.")
