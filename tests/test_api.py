"""
Tests for FastAPI endpoints.
"""
import pytest
import json
from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_json_document():
    """Sample JSON document."""
    return json.dumps({
        "text": "Python is a programming language. It is widely used for web development, data science, and automation.",
        "title": "Python Introduction"
    }).encode('utf-8')


@pytest.fixture
def sample_questions():
    """Sample questions JSON."""
    return json.dumps({
        "questions": [
            "What is Python?",
            "What is Python used for?"
        ]
    }).encode('utf-8')


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_qa_endpoint_missing_files(client):
    """Test QA endpoint with missing files."""
    response = client.post("/qa")
    assert response.status_code != 200


def test_qa_endpoint_invalid_questions_format(client, sample_json_document):
    """Test QA endpoint with invalid questions format."""
    files = {
        "document": ("test.json", BytesIO(sample_json_document), "application/json"),
        "questions_file": ("questions.json", BytesIO(b"invalid json"), "application/json")
    }
    response = client.post("/qa", files=files)
    assert response.status_code == 400

