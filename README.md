# railway-iot-ml-engine

Machine learning engine for anomaly detection in **railway-iot-platform**.

---

## Responsibilities

- Anomaly detection on sensor time-series using Isolation Forest
- REST inference API (FastAPI sidecar)
- API key authentication for all inference endpoints

---

## Stack

| Component | Library / Version |
|---|---|
| API framework | FastAPI |
| ASGI server | Uvicorn |
| ML library | scikit-learn |
| Numerical | NumPy |
| Validation | Pydantic v2 |

---

## Implemented Model

| Model | Algorithm | Input | Output |
|---|---|---|---|
| Anomaly detector | Isolation Forest | Array of float sensor values | `is_anomaly: bool`, `score: float` per value |

---

## API Endpoints

### Authentication

All inference endpoints require:
```
X-Api-Key: <ML_API_KEY>
```

The key is configured via the `ML_API_KEY` environment variable. Requests with a missing or invalid key receive `403 Forbidden`.

### Endpoints

```
GET  /api/v1/anomaly/health         Health check (no auth required)
POST /api/v1/anomaly/detect/        Run anomaly detection
```

### Detect Request / Response

```json
POST /api/v1/anomaly/detect/
Headers: X-Api-Key: <key>

{
  "metric": "temperature",
  "values": [65.1, 66.3, 84.2, 67.0, 68.5]
}
```

```json
{
  "results": [
    {"value": 65.1, "is_anomaly": false, "score": 0.12},
    {"value": 84.2, "is_anomaly": true,  "score": -0.31}
  ]
}
```

Validation rules:
- `metric` must be one of: `temperature`, `vibration`, `rpm`, `brake-pressure`, `load-weight`
- `values` must be a non-empty array with at most **1,000** elements

---

## Security

- API key validated via `APIKeyHeader` (FastAPI security dependency)
- `ML_API_KEY` read from environment — no hardcoded default
- Metric name and input size validated before running inference
- No user-controlled URLs or file paths accepted

---

## Local Dev (without Docker)

```bash
pip install -r requirements.txt

export ML_API_KEY=your-dev-key
uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload
```

API docs available at **http://localhost:8004/docs** (Swagger UI).

---

## Docker

```bash
docker compose build ml
docker compose up -d ml
```

Service listens on port **8004** internally; routed from Nginx at `/ml/`.
