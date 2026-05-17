from sqlalchemy.orm import Session

from app.models import WeatherQuery
from app.schemas import WeatherData


def save_query(db: Session, data: WeatherData) -> WeatherQuery:
    record = WeatherQuery(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history(db: Session) -> list[WeatherQuery]:
    return (
        db.query(WeatherQuery)
        .order_by(WeatherQuery.queried_at.desc())
        .all()
    )


def delete_query(db: Session, query_id: int) -> bool:
    record = db.query(WeatherQuery).filter(WeatherQuery.id == query_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
