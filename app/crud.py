from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.models import WeatherQuery
from app.schemas import WeatherData


def get_recent_query(db: Session, city: str, minutes: int = 5) -> WeatherQuery | None:
    cutoff = datetime.now() - timedelta(minutes=minutes)
    return (
        db.query(WeatherQuery)
        .filter(
            func.lower(WeatherQuery.city) == city.lower(),
            WeatherQuery.queried_at >= cutoff,
        )
        .order_by(WeatherQuery.queried_at.desc())
        .first()
    )


def save_query(
    db: Session, data: WeatherData, from_cache: bool = False
) -> WeatherQuery:
    record = WeatherQuery(**data.model_dump(), from_cache=from_cache)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _apply_history_filters(
    query: Query,
    city: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> Query:
    if city:
        query = query.filter(func.lower(WeatherQuery.city).contains(city.lower()))
    if date_from:
        query = query.filter(WeatherQuery.queried_at >= date_from)
    if date_to:
        query = query.filter(WeatherQuery.queried_at <= date_to)
    return query


def get_history(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    city: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[WeatherQuery], int]:
    query = _apply_history_filters(db.query(WeatherQuery), city, date_from, date_to)
    total = query.count()
    items = (
        query.order_by(WeatherQuery.queried_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_all_history(
    db: Session,
    city: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[WeatherQuery]:
    query = _apply_history_filters(db.query(WeatherQuery), city, date_from, date_to)
    return query.order_by(WeatherQuery.queried_at.desc()).all()


def delete_query(db: Session, query_id: int) -> bool:
    record = db.query(WeatherQuery).filter(WeatherQuery.id == query_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
