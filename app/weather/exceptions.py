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

