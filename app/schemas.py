from datetime import datetime

from pydantic import BaseModel


class WeatherData(BaseModel):
    city: str
    temperature: float
    feels_like: float
    description: str
    humidity: int
    wind_speed: float


class WeatherQueryResponse(WeatherData):
    id: int
    queried_at: datetime

    model_config = {"from_attributes": True}


class PaginatedHistory(BaseModel):
    items: list[WeatherQueryResponse]
    total: int
    page: int
    page_size: int
    pages: int
