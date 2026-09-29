import src.app as app_module
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Debate Club": {
            "description": "Practice public speaking",
            "schedule": "Mondays at 3:30 PM",
            "max_participants": 10,
            "participants": ["existing@mergington.edu"],
        },
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 12,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Debate Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[expected_activity]["participants"] == ["existing@mergington.edu"]
    assert response.json()[expected_activity]["max_participants"] == 10


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Debate Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Debate%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        "/activities/Debate%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert app_module.activities["Debate Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Debate Club"
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/Debate%20Club/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Unknown%20Club/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unknown_participant(client):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Debate%20Club/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}