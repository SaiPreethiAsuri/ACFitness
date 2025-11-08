import pytest
from app import app, workouts

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Clear workouts before each test
        for k in list(workouts.keys()):
            workouts[k].clear()
        yield client

def test_home_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"ACEest" in resp.data  # Partial match (more robust)

def test_add_valid_workout(client):
    """POST a valid workout to /add_workout"""
    resp = client.post("/add_workout", data={
        "category": "Workout",
        "workout": "Pushups",
        "duration": "30"
    }, follow_redirects=True)
    assert resp.status_code == 200
    # Relaxed flash message check
    assert b"Pushups" in resp.data
    assert b"successfully" in resp.data
    assert len(workouts["Workout"]) == 1

def test_add_workout_missing_fields(client):
    resp = client.post("/add_workout", data={
        "category": "Workout",
        "workout": "",
        "duration": "30"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Please enter" in resp.data
    assert len(workouts["Workout"]) == 0

def test_add_workout_invalid_duration(client):
    resp = client.post("/add_workout", data={
        "category": "Workout",
        "workout": "Situps",
        "duration": "abc"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Duration must be" in resp.data
    assert len(workouts["Workout"]) == 0

def test_summary_page_empty(client):
    """When no workouts exist, show total=0 and a 'no sessions' message"""
    resp = client.get("/summary")
    assert resp.status_code == 200
    assert b"Total Time Spent: 0" in resp.data
    assert b"No sessions logged yet!" in resp.data

def test_summary_page_with_workouts(client):
    client.post("/add_workout", data={
        "category": "Warm-up",
        "workout": "Jogging",
        "duration": "20"
    }, follow_redirects=True)
    client.post("/add_workout", data={
        "category": "Workout",
        "workout": "Pushups",
        "duration": "40"
    }, follow_redirects=True)

    resp = client.get("/summary")
    assert resp.status_code == 200
    assert b"Jogging" in resp.data
    assert b"Pushups" in resp.data
    assert b"Total Time Spent" in resp.data
    assert b"Excellent" in resp.data  # partial match for motivation
