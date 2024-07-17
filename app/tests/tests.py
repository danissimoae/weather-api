import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_home():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/weather/")
    assert response.status_code == 200
    assert "Weather App" in response.text

@pytest.mark.asyncio
async def test_autocomplete():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/weather/autocomplete?query=New")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_weather():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/weather/", json={"city_data": "New York"})
    assert response.status_code == 200
    assert "Weather for New York" in response.text
