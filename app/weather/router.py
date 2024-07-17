import datetime
import logging

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
import httpx
from geopy.geocoders import Nominatim
from pydantic import BaseModel
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime


router = APIRouter(
    prefix="/weather",
    tags=["Погода"],
)

templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)
geolocator = Nominatim(user_agent="weather_app")


class CityData(BaseModel):
    city_data: str


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.post("/")
async def get_weather(request: Request, city_data: CityData):
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

        return templates.TemplateResponse("weather.html",
                                          {"request": request, "city": city_data, "weather_data": weather_data,
                                           "current_time": current_time})
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise FetchingDataException



from fastapi import HTTPException, status


class WeatherException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class CityNotFoundException(WeatherException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Город не найден / City not found :("


class TimeZoneNotFoundException(WeatherException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Временной пояс не найден / Timezone not found :("


class FetchingDataException(WeatherException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка получения данных / Fetching data error :("

