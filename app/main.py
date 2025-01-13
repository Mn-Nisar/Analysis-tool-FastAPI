from fastapi import Depends, FastAPI
from functools import lru_cache
from app.api.endpoints import aws , analysis, visualization, healthcheck ,auth
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from . import config

origins = [
    "http://localhost:3000",  
    "http://www.ciods.in",
    "https://www.ciods.in",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],   
    allow_headers=["*"], 
)

@lru_cache
def get_settings():
    return config.Settings()

user_dependecy = Annotated[dict, Depends(auth.get_current_user)]


@app.get("/info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
    }

@app.get("/protected-route")
async def protected_route(user: user_dependecy):
    return {"message": f"Hello, {user}. You are authenticated!"}

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(visualization.router, prefix="/visualization", tags=["Visualization"])
app.include_router(aws.router, prefix="/aws", tags=["aws"])


