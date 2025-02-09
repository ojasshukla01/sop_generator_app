import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
import os
from fastapi import FastAPI

# Initialize Sentry with DSN from environment variables
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),  # Use the DSN from your environment
    integrations=[StarletteIntegration()],
    traces_sample_rate=1.0  # Adjust sampling rate for performance monitoring
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Sentry is integrated successfully!"}
