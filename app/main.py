from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from weather.router import router as weather_router

app = FastAPI()
app.include_router(weather_router)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Access-Authorization",
                   "Access-Control-Allow-Headers",
                   "Set-Cookie"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)