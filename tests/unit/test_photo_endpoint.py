from fastapi.testclient import TestClient

from frameflow.api.app import app


def test_next_photo_not_implemented() -> None:
    client = TestClient(app)

    response = client.get("/photos/next")

    assert response.status_code == 501
    assert response.json() == {"detail": "Photo selection service not yet wired."}
