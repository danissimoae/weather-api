from pydantic import BaseModel

class CitySchema(BaseModel):
    city: str