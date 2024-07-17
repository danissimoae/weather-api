import datetime
from datetime import datetime

import pytz
import requests
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from app.weather.exceptions import *
from app.weather.schemas import CityData

router = APIRouter(
    prefix="/weather",
    tags=["Погода"],
)

templates = Jinja2Templates(directory="app/templates")
geolocator = Nominatim(user_agent="weather_app")


@router.get("/")
async def home(request: Request):
    """Домашняя страница /weather (GET)"""
    last_city = request.cookies.get("last_city")
    if last_city:
        last_city = last_city.encode('latin-1').decode('utf-8')
    return templates.TemplateResponse("home.html", {"request": request, "last_city": last_city})


@router.post("/")
async def get_weather(request: Request, city_data: CityData):
    """Роут отвечающий за получение данных /weather (POST)"""
    location = geolocator.geocode(city_data.city_data)
    if location is None:
        raise CityNotFoundException

    timezone_finder = TimezoneFinder()
    timezone_result = timezone_finder.timezone_at(lat=location.latitude, lng=location.longitude)
    if timezone_result is None:
        raise TimeZoneNotFoundException

    timezone_pytz = pytz.timezone(timezone_result)
    local_time = datetime.now(timezone_pytz)
    current_time = local_time.strftime("%I:%M %p")

    try:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m"
            f"&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m"
            f"&daily=uv_index_max&timezone=auto"
        )
        response.raise_for_status()
        weather_data = response.json()
    except requests.RequestException as e:
        raise FetchingDataException

    response = templates.TemplateResponse("weather.html", {"request": request, "city": city_data.city_data,
                                                           "weather_data": weather_data, "current_time": current_time})
    response.set_cookie(key="last_city", value=city_data.city_data.encode('utf-8').decode('latin-1'))
    return response


@router.get("/autocomplete")
async def autocomplete(query: str):
    """Роут для получения данных для подсказок в строке /autocomplete (GET)"""
    locations = geolocator.geocode(query, exactly_one=False, limit=5)
    suggestions = [location.address for location in locations] if locations else []
    return JSONResponse(content=suggestions)
