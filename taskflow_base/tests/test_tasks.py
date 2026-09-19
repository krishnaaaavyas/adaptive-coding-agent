import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _make_project(name="Test Project") -> dict:
    response = client.post("/projects", json={"name": name})
    assert response.status_code == 200
    return response.json()


class TestCreateTask:
    def test_creates_task_with_valid_payload(self):
        # Arrange
        project = _make_project()

        # Act
        response = client.post(
            "/tasks",
            json={"title": "Write onboarding doc", "project_id": 1, "tags": ["Docs", " docs ", "URGENT"]},
        )

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["title"] == "Write onboarding doc"
        assert body["tags"] == ["docs", "urgent"]  # normalized: trimmed, lowercased, deduped

    def test_rejects_empty_title(self):
        # Arrange
        _make_project()

        # Act
        response = client.post("/tasks", json={"title": "   ", "project_id": 1, "tags": []})

        # Assert
        assert response.status_code == 422

    def test_rejects_unknown_project(self):
        # Arrange — no project created

        # Act
        response = client.post("/tasks", json={"title": "Orphan task", "project_id": 999, "tags": []})

        # Assert
        assert response.status_code == 404

    def test_public_id_is_a_uuid_not_internal_pk(self):
        # Arrange
        _make_project()

        # Act
        response = client.post("/tasks", json={"title": "Check DTO shape", "project_id": 1, "tags": []})

        # Assert
        body = response.json()
        assert "id" not in body
        assert "public_id" in body
