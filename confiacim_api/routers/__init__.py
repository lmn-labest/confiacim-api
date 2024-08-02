from confiacim_api.routers.admin import router as admin_router
from confiacim_api.routers.auth import router as auth_router
from confiacim_api.routers.base import router as base_router
from confiacim_api.routers.case import router as case_router
from confiacim_api.routers.tencim import router as tencim_router
from confiacim_api.routers.users import router as user_router

__all__ = (
    "auth_router",
    "base_router",
    "case_router",
    "user_router",
    "admin_router",
    "tencim_router",
)
