from unittest.mock import AsyncMock, patch

from app import crud
from app.schemas import WeatherData

MOCK_WEATHER = WeatherData(
    city="London",
    temperature=15.0,
    feels_like=13.0,
    description="cloudy",
    humidity=70,
    wind_speed=4.0,
    unit="metric",
)


def test_rate_limit_returns_429(client):
    with patch(
        "app.routers.weather.fetch_weather",
        new=AsyncMock(return_value=MOCK_WEATHER),
    ):
        r1 = client.get("/api/weather?city=London")
        r2 = client.get("/api/weather?city=London")
        r3 = client.get("/api/weather?city=London")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 429
        assert "Too many requests" in r3.json()["detail"]


def test_rate_limit_prevents_db_write(client, db):
    with patch(
        "app.routers.weather.fetch_weather",
        new=AsyncMock(return_value=MOCK_WEATHER),
    ):
        for _ in range(3):
            client.get("/api/weather?city=London")

        _, total = crud.get_history(db)
        assert total == 2
