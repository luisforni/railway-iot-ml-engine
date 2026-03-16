import numpy as np
from fastapi import APIRouter, HTTPException

from schema import PredictRequest, PredictResponse
from services.trainer import load_model

router = APIRouter(prefix="/predict", tags=["anomaly"])

_MAX_VALUES = 1000
_VALID_METRICS = {"temperature", "vibration", "rpm", "brake-pressure", "load-weight"}

@router.post("/", response_model=PredictResponse)
def predict(request: PredictRequest):
    if request.metric not in _VALID_METRICS:
        raise HTTPException(status_code=422, detail=f"Unknown metric '{request.metric}'.")

    if not request.values:
        raise HTTPException(status_code=422, detail="values list must not be empty.")

    if len(request.values) > _MAX_VALUES:
        raise HTTPException(status_code=422, detail=f"values list exceeds limit of {_MAX_VALUES}.")

    model = load_model(request.metric)
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model for '{request.metric}' not trained yet.",
        )

    n = len(request.values)
    hours = request.hours if len(request.hours) == n else [12.0] * n
    dows  = request.dows  if len(request.dows)  == n else [1.0]  * n

    X = np.array(list(zip(request.values, hours, dows)), dtype=float)
    predictions = model.predict(X).tolist()
    scores = model.score_samples(X).tolist()

    return PredictResponse(metric=request.metric, predictions=predictions, scores=scores)

@router.post("/train", tags=["anomaly"])
def trigger_training():
    from services.trainer import train_all
    results = train_all()
    return {"trained": results}
