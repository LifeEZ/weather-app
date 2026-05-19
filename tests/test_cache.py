from unittest.mock import AsyncMock, patch

from app.schemas import WeatherData

MOCK_LONDON = WeatherData(
    city="London",
    temperature=15.0,
    feels_like=13.0,
    description="light rain",
    humidity=80,
    wind_speed=5.0,
    unit="metric",
)

MOCK_PARIS = WeatherData(
    city="Paris",
    temperature=20.0,
    feels_like=18.0,
    description="clear sky",
    humidity=55,
    wind_speed=3.0,
    unit="metric",
)


def test_second_request_served_from_cache(client):
    with patch(
        "app.routers.weather.fetch_weather",
        new=AsyncMock(return_value=MOCK_LONDON),
    ) as mock_fetch:
        r1 = client.get("/api/weather?city=London")
        r2 = client.get("/api/weather?city=London")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["from_cache"] is False
        assert r2.json()["from_cache"] is True
        mock_fetch.assert_called_once()


def test_different_cities_both_fetch_live(client):
    async def mock_fetch(city, unit="metric"):
        return MOCK_LONDON if city == "London" else MOCK_PARIS

    with patch(
        "app.routers.weather.fetch_weather", new=mock_fetch
    ) as mock:
        r1 = client.get("/api/weather?city=London")
        r2 = client.get("/api/weather?city=Paris")

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["from_cache"] is False
        assert r2.json()["from_cache"] is False
