from confiacim_api.routes.admin import router as admin_router
from confiacim_api.routes.auth import router as auth_router
from confiacim_api.routes.base import router as base_router
from confiacim_api.routes.case import router as case_router
from confiacim_api.routes.users import router as user_router

__all__ = (
    "auth_router",
    "base_router",
    "case_router",
    "user_router",
    "admin_router",
)
