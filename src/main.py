import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader

from routers import anomaly, health
from scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

_API_KEY = os.environ.get("ML_API_KEY", "")
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str | None = Security(_api_key_header)):
    if not _API_KEY:
        return
    if key != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key.",
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ML Engine starting up — initializing scheduler")
    start_scheduler()
    yield
    logger.info("ML Engine shutting down")

app = FastAPI(
    title="Railway IoT ML Engine",
    description="Anomaly detection and predictive maintenance for railway sensors",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(
    anomaly.router,
    dependencies=[Security(verify_api_key)],
)
