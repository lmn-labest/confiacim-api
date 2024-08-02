from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from confiacim_api.conf import settings
from confiacim_api.routers import (
    admin_router,
    auth_router,
    base_router,
    case_router,
    tencim_router,
    user_router,
)

app = FastAPI(
    title="Confiacim API",
    description="Backend da aplicação do confiacim",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

if settings.CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(base_router)
app.include_router(case_router)
app.include_router(user_router)
app.include_router(tencim_router)


@app.exception_handler(RequestValidationError)
async def validation_exeception_handler(request: Request, exec: RequestValidationError):
    new_errors = [
        {
            "type": e["type"],
            "msg": e["msg"],
            "input": e["input"],
            "loc": e["loc"],
        }
        for e in exec.errors()
    ]
    return JSONResponse({"detail": new_errors}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
