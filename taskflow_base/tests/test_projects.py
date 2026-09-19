from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestCreateProject:
    def test_creates_project_with_valid_payload(self):
        # Arrange — nothing to arrange

        # Act
        response = client.post("/projects", json={"name": "Q4 Roadmap"})

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Q4 Roadmap"

    def test_rejects_empty_name(self):
        # Arrange — nothing to arrange

        # Act
        response = client.post("/projects", json={"name": "   "})

        # Assert
        assert response.status_code == 422

    def test_public_id_is_a_uuid_not_internal_pk(self):
        # Arrange — nothing to arrange

        # Act
        response = client.post("/projects", json={"name": "Check DTO shape"})

        # Assert
        body = response.json()
        assert "id" not in body
        assert "public_id" in body
