from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from confiacim_api import __version__
from confiacim_api.conf import settings
from confiacim_api.errors import UploadCaseBaseError
from confiacim_api.routers import (
    admin_router,
    auth_router,
    base_router,
    case_router,
    form_router,
    tencim_router,
    user_router,
    variable_group_router,
)

app = FastAPI(
    title="Confiacim API",
    version=__version__,
    description="Backend da aplicação do confiacim",
    redoc_url=None,
    docs_url=None,
    openapi_url="/api/openapi.json",
)

add_pagination(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

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
app.include_router(form_router)
app.include_router(variable_group_router)


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


@app.exception_handler(UploadCaseBaseError)
async def upload_exeception_handler(request: Request, exec: UploadCaseBaseError):
    return JSONResponse({"detail": str(exec)}, status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/js/swagger-ui-bundle.js",
        swagger_css_url="/static/css/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()
