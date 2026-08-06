from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_and_login_flow() -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert register_response.status_code == 200
    body = register_response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
