import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from fastapi.testclient import TestClient

# Set APP_ENV for testing
os.environ["APP_ENV"] = "testing"

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "APP_ENV is currently set to: testing" in response.json()["message"]
