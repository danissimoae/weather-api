import datetime
import logging
import httpx
import pytz

from datetime import datetime
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from geopy.geocoders import Nominatim
from fastapi.responses import JSONResponse
from timezonefinder import TimezoneFinder
from typing_extensions import List

from app.weather.exceptions import *
from app.weather.schemas import CityData

router = APIRouter(
    prefix="/weather",
    tags=["Погода"],
)

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)
geolocator = Nominatim(user_agent="weather_app")

@router.get("/")
async def home(request: Request):
    """Главная страница"""
    last_city = request.cookies.get("last_city")
    return templates.TemplateResponse("home.html", {"request": request,
                                                    "last_city": last_city})


@router.post("/")
async def get_weather(request: Request, city_data: CityData):
    """Post-запрос для получения данных о погоде"""
    try:
        location = geolocator.geocode(city_data.city_data)
        if location is None:
            raise CityNotFoundException
        timezone_finder = TimezoneFinder()
        timezone_result = timezone_finder.timezone_at(lat=location.latitude, lng=location.longitude)
        if timezone_result is None:
            raise TimeZoneNotFoundException
        local_time = datetime.now(pytz.timezone(timezone_result))
        current_time = local_time.strftime("%I: %M %p")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,soil_temperature_0cm,uv_index,is_day&daily=uv_index_max&timezone=auto")
            response.raise_for_status()
            weather_data = response.json()

        response = templates.TemplateResponse("weather.html",
                                              {"request": request,
                                               "city": city_data,
                                               "weather_data": weather_data,
                                               "current_time": current_time
                                               })
        response.set_cookie("last_city", city_data.city_data)
        return response

    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise FetchingDataException



@router.get("/autocomplete", response_model=List[str])
async def autocomplete(city: str = Query(...)):
    """Подсказки для поиска"""
    locations = geolocator.geocode(city,
                                   exactly_one=False,
                                   limit=3)
    suggestions = [location.address for location in locations] if locations else []
    return JSONResponse(content=suggestions)