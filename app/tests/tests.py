from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_homepage():
    response = client.get("/weather/")
    assert response.status_code == 200
    assert b"Weather App" in response.content

def test_get_weather():
    response = client.post("/weather/", json={"city_data": "New York"})
    assert response.status_code == 200
    assert b"Weather for New York" in response.content

def test_autocomplete():
    response = client.get("/weather/autocomplete?city=New")
    assert response.status_code == 200
    suggestions = response.json()
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0