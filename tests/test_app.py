from fastapi.testclient import TestClient

from src.app import activities, app


class TestActivitiesAPI:
    def test_root_redirects_to_static_page(self, client: TestClient):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location

    def test_get_activities_returns_activity_data(self, client: TestClient):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert activity_name in response_data
        assert response_data[activity_name]["participants"]

    def test_signup_adds_participant_to_activity(self, client: TestClient):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == (
            f"Signed up {email} for {activity_name}"
        )
        assert email in activities[activity_name]["participants"]

    def test_duplicate_signup_returns_error_without_duplicating_participant(
        self, client: TestClient
    ):
        # Arrange
        activity_name = "Chess Club"
        email = "existingstudent@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        participant_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student is already signed up for this activity"
        )
        assert len(activities[activity_name]["participants"]) == participant_count

    def test_signup_for_unknown_activity_returns_not_found(
        self, client: TestClient
    ):
        # Arrange
        activity_name = "Unknown Activity"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_removes_participant_from_activity(
        self, client: TestClient
    ):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert response.json()["message"] == (
            f"Unregistered {email} from {activity_name}"
        )

    def test_unregister_unknown_participant_returns_not_found(
        self, client: TestClient
    ):
        # Arrange
        activity_name = "Chess Club"
        email = "unknown@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_unregister_unknown_activity_returns_not_found(
        self, client: TestClient
    ):
        # Arrange
        activity_name = "Unknown Activity"
        email = "unknown@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
