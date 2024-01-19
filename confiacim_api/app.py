from fastapi import FastAPI

from confiacim_api.routes import base_router, celery_router, simulation_router

app = FastAPI()

app.include_router(base_router)
app.include_router(simulation_router)
app.include_router(celery_router)
