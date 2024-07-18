import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_home():
    response = client.get("/weather/")
    assert response.status_code == 200
    assert "Прогноз погоды" in response.text


@pytest.mark.asyncio
async def test_autocomplete():
    response = client.get("/weather/autocomplete?query=New")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_weather_valid_city():
    response = client.post("/weather/", json={"city_data": "New York"})
    assert response.status_code == 200
    assert "Погода в New York" in response.text


@pytest.mark.asyncio
async def test_get_weather_invalid_city():
    response = client.post("/weather/", json={"city_data": "InvalidCityName"})
    assert response.status_code == 404
    assert "City not found" in response.json().get("message")


@pytest.mark.asyncio
async def test_get_weather_no_city():
    response = client.post("/weather/", json={"city_data": ""})
    assert response.status_code == 404
    assert "City not found" in response.json().get("message")
