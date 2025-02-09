import sentry_sdk
from sentry_sdk.integrations.asgi import ASGIIntegration
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    integrations=[ASGIIntegration()],
    traces_sample_rate=1.0  # Adjust this for sampling traces
)

app = FastAPI()

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
