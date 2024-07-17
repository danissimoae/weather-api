from pydantic import BaseModel


class CityData(BaseModel):
    city_data: str