from pydantic import BaseModel

class PredictRequest(BaseModel):
    metric: str
    values: list[float]
    hours: list[float] = []
    dows: list[float] = []

class PredictResponse(BaseModel):
    metric: str
    predictions: list[int]
    scores: list[float]

class HealthResponse(BaseModel):
    status: str
    trained_models: list[str]
    total_models: int
