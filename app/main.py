import time

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.database import engine
from app.logger import logger
from app.models import Base
from app.routers import health, weather

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Weather App")
app.state.limiter = limiter


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info("", extra={
        "event": "request_start",
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown",
    })

    response = await call_next(request)

    duration_ms = round((time.time() - start) * 1000)
    logger.info("", extra={
        "event": "request_end",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    })
    return response


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning("", extra={
        "event": "error",
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown",
        "detail": "rate limit exceeded",
        "status_code": 429,
    })
    return JSONResponse(
        status_code=429,
        content={
            "detail": (
                "Too many requests. You can search up to 30 times per minute."
            )
        },
    )


app.include_router(weather.router)
app.include_router(health.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("app/static/index.html")
