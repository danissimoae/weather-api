from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import logging
import os

from app.config import Config
from app.weather.exceptions import general_exception_handler
from app.weather.router import router as weather_router

# Для получения зависимостей, ценных переменных или ключей
config = Config()


app = FastAPI(
    title="Weather API",
    description="API для получения данных о погоде",
    openapi_url=config.OPENAPI_URL
)
app.include_router(weather_router)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Регистрация обработчиков исключений
app.add_exception_handler(Exception, general_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# https://github.com/danissimoae