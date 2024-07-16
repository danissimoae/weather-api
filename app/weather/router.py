import datetime
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import httpx
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime


router = APIRouter(
    prefix="/weather",
    tags=["Погода"],
)

templates = Jinja2Templates(directory="templates")

geolocator = Nominatim(user_agent="weather_app")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.post("/")
async def get_weather(request: Request, city_data: str):
    location = geolocator.geocode(city_data)
    timezone_finder = TimezoneFinder()
    timezone_result = timezone_finder.timezone_at(lat=location.latitude, lng=location.longitude)
    home = pytz.timezone(timezone_result)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I: %M %p")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,soil_temperature_0cm,uv_index,is_day&daily=uv_index_max&timezone=auto")
        weather_data = response.json()
        return templates.TemplateResponse("weather.html", {"request": request, "city": city_data, "weather_data": weather_data})