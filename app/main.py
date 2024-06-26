from fastapi import FastAPI
import logging
import logging.config
from app.routers import category_routes

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(category_routes.router, prefix="/api/category", tags=["Category"])
