# exceptions.py
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class WeatherException(HTTPException):
    """Базовый класс для создания кастомных исключений"""
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


async def general_exception_handler(request, exc):
    logger.error(f"Ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content={"Сообщение": "Произошла непредвиденная ошибка"},
    )
