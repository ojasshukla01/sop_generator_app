import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration  # Correct integration for FastAPI
from fastapi import FastAPI

# Initialize Sentry with StarletteIntegration
sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    integrations=[StarletteIntegration()],
    traces_sample_rate=1.0  # Adjust sampling rate as needed
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Sentry is integrated!"}
