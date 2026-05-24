import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert expected_activity in response_data
    assert isinstance(response_data[expected_activity]["participants"], list)
    assert response_data[expected_activity]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"

    assert new_email not in client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {new_email} for {activity_name}"
    }
    assert new_email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_for_activity_returns_400_when_already_registered():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "daniel@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Already registered"


def test_remove_participant_removes_existing_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    assert participant_email in client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {participant_email} from {activity_name}"
    }
    assert participant_email not in client.get("/activities").json()[activity_name]["participants"]


def test_remove_participant_returns_404_when_missing():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@student.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
