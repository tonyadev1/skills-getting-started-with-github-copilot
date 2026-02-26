from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


def setup_module(module):
    # ensure activities are in their initial state for each test run
    # we just reset the participants to known values
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        }
    })


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_success():
    email = "new@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    # re-use an existing participant
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=foo@bar.com")
    assert response.status_code == 404


def test_remove_signup_success():
    email = "daniel@mergington.edu"
    response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_remove_signup_not_signed():
    response = client.delete("/activities/Chess Club/signup?email=absent@mergington.edu")
    assert response.status_code == 404


def test_remove_signup_nonexistent_activity():
    response = client.delete("/activities/Nope/signup?email=foo@bar.com")
    assert response.status_code == 404
