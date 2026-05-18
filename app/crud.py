from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import WeatherQuery
from app.schemas import WeatherData


def save_query(db: Session, data: WeatherData) -> WeatherQuery:
    record = WeatherQuery(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    city: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[WeatherQuery], int]:
    query = db.query(WeatherQuery)

    if city:
        query = query.filter(func.lower(WeatherQuery.city).contains(city.lower()))
    if date_from:
        query = query.filter(WeatherQuery.queried_at >= date_from)
    if date_to:
        query = query.filter(WeatherQuery.queried_at <= date_to)

    total = query.count()
    items = (
        query.order_by(WeatherQuery.queried_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def delete_query(db: Session, query_id: int) -> bool:
    record = db.query(WeatherQuery).filter(WeatherQuery.id == query_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
