from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint() -> None:
    with TestClient(create_app(initialize_db=False)) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_web_interface_is_served() -> None:
    with TestClient(create_app(initialize_db=False)) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Production RAG Assistant" in response.text


def test_question_validation() -> None:
    with TestClient(create_app(initialize_db=False)) as client:
        response = client.post("/api/v1/chat/ask", json={"question": "x"})

    assert response.status_code == 422
