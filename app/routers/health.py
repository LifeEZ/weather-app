import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["health"])

OWM_HEALTH_URL = "https://api.openweathermap.org"


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    owm_status = "ok"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OWM_HEALTH_URL, timeout=2.0)
        if response.status_code >= 500:
            owm_status = "unreachable"
    except Exception:
        owm_status = "unreachable"

    if db_status == "unreachable":
        overall = "unhealthy"
    elif owm_status == "unreachable":
        overall = "degraded"
    else:
        overall = "healthy"

    status_code = 503 if overall == "unhealthy" else 200

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "database": db_status,
            "weather_api": owm_status,
        },
    )
