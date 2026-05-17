from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine
from app.models import Base
from app.routers import weather

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weather App")

app.include_router(weather.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("app/static/index.html")
