import time

import httpx
from fastapi import HTTPException

from app.config import settings
from app.logger import logger
from app.schemas import WeatherData

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather"


async def fetch_weather(city: str, unit: str = "metric") -> WeatherData:
    params = {
        "q": city,
        "appid": settings.openweathermap_api_key,
        "units": unit,
    }

    start = time.time()
    async with httpx.AsyncClient() as client:
        response = await client.get(OPENWEATHERMAP_URL, params=params)
    duration_ms = round((time.time() - start) * 1000)

    if response.status_code != 200:
        log_fn = logger.warning if response.status_code == 404 else logger.error
        log_fn("", extra={
            "event": "weather_api_error",
            "city": city,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        })
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid API key.")
        raise HTTPException(status_code=502, detail="Weather service unavailable.")

    logger.info("", extra={
        "event": "weather_api_call",
        "city": city,
        "unit": unit,
        "duration_ms": duration_ms,
        "status": "ok",
    })

    data = response.json()

    return WeatherData(
        city=data["name"],
        temperature=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        description=data["weather"][0]["description"],
        humidity=data["main"]["humidity"],
        wind_speed=data["wind"]["speed"],
        unit=unit,
    )
