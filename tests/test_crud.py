from datetime import datetime, timedelta

import pytest

from app import crud
from app.schemas import WeatherData


def make_weather(city: str, unit: str = "metric") -> WeatherData:
    return WeatherData(
        city=city,
        temperature=15.0,
        feels_like=13.0,
        description="clear",
        humidity=70,
        wind_speed=3.0,
        unit=unit,
    )


@pytest.fixture
def sample_data(db):
    for city, unit in [
        ("London", "metric"),
        ("London", "imperial"),
        ("Paris", "metric"),
        ("Tokyo", "metric"),
    ]:
        crud.save_query(db, make_weather(city, unit))
    return db


def test_filter_by_city_case_insensitive(sample_data):
    items, total = crud.get_history(sample_data, city="lon")
    assert total == 2
    assert all("london" in item.city.lower() for item in items)


def test_filter_by_date_from_excludes_past(sample_data):
    future = datetime.now() + timedelta(hours=1)
    _, total = crud.get_history(sample_data, date_from=future)
    assert total == 0


def test_filter_by_date_to_excludes_future(sample_data):
    past = datetime.now() - timedelta(hours=1)
    _, total = crud.get_history(sample_data, date_to=past)
    assert total == 0


def test_pagination_splits_results(sample_data):
    page1, total = crud.get_history(sample_data, page=1, page_size=2)
    page2, _ = crud.get_history(sample_data, page=2, page_size=2)

    assert total == 4
    assert len(page1) == 2
    assert len(page2) == 2
    assert {i.id for i in page1}.isdisjoint({i.id for i in page2})


def test_get_all_history_returns_everything(sample_data):
    items = crud.get_all_history(sample_data)
    assert len(items) == 4
