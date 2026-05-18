from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WeatherQuery(Base):
    __tablename__ = "weather_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    feels_like: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    queried_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    from_cache: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unit: Mapped[str] = mapped_column(String, default="metric", nullable=False)
