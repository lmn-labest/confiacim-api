from confiacim_api.routes.base import router as base_router
from confiacim_api.routes.celery import router as celery_router
from confiacim_api.routes.simulation import router as simulation_router

__all__ = (
    "base_router",
    "simulation_router",
    "celery_router",
)
