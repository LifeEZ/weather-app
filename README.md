# Weather App

A web application for checking current weather by city name, built using FastAPI and PostgreSQL.

Requires **Python 3.13** and **Docker Desktop**.

## Features

- Search current weather for any city via OpenWeatherMap API
- Toggle between Celsius and Fahrenheit
- Caches repeated city queries within 5 minutes
- Stores every query in a PostgreSQL database with pagination and filtering
- Export query history as CSV
- Delete individual history entries
- Per-IP rate limiting on the weather endpoint
- JSON logging to stdout

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, psycopg2, Alembic
- **Database:** PostgreSQL
- **Frontend:** HTML, Bootstrap, JavaScript
- **Infrastructure:** Docker, Docker Compose

## Quickstart

```bash
git clone https://github.com/LifeEZ/weather-app.git
cd weather-app
cp .env.example .env        # Windows: copy .env.example .env
# open .env and add your OpenWeatherMap API key
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
DATABASE_URL=postgresql://weather_user:weather_pass@db:5432/weatherdb
RATE_LIMIT=30/minute
```

`RATE_LIMIT` is optional. Default is `30/minute` if not set.

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## API Endpoints

- `GET /api/weather?city=London&unit=metric` - fetch current weather and save to history
- `GET /api/history` - paginated history with optional city and date filters
- `GET /api/history/export` - download filtered history as CSV
- `DELETE /api/history/{id}` - delete a history entry
- `GET /health` - service health check

Full interactive docs available at [http://localhost:8000/docs](http://localhost:8000/docs)
