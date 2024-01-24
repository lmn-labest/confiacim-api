from fastapi import FastAPI

from confiacim_api.routes import base_router, celery_router, simulation_router

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins="http://localhost:5173",
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(base_router)
app.include_router(simulation_router)
app.include_router(celery_router)
