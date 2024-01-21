from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from confiacim_api.routes import base_router, celery_router, simulation_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base_router)
app.include_router(simulation_router)
app.include_router(celery_router)
