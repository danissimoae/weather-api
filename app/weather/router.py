import datetime
import logging
from datetime import datetime

import httpx
import pytz
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from geopy.geocoders import Nominatim
from pydantic import BaseModel
from timezonefinder import TimezoneFinder

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

