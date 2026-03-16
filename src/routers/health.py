import os

from fastapi import APIRouter

from schema import HealthResponse
from services.trainer import MODELS_DIR

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health():
    trained: list[str] = []
    if os.path.exists(MODELS_DIR):
        trained = [
            f.replace(".joblib", "").replace("_", "-")
            for f in sorted(os.listdir(MODELS_DIR))
            if f.endswith(".joblib")
        ]
    return HealthResponse(
        status="ok",
        trained_models=trained,
        total_models=len(trained),
    )
