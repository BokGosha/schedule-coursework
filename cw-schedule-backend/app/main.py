from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.core.config import get_settings
from app.api.v1.api import api_router
from app.core.logger import logger
from app.db.init_db import init_db

settings = get_settings()

app = FastAPI(
    title="Schedule API",
    description="API for managing schedules",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")


@app.get("/")
async def root():
    return {"message": "Welcome to Schedule API"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Schedule API - Swagger UI",
    )
