import pytest
from app.app import app, workouts


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    """Ensure the main tabbed interface loads"""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"ACEest Fitness & Gym Tracker" in resp.data
    assert b"Log Workouts" in resp.data
    assert b"Workout Chart" in resp.data
    assert b"Diet Chart" in resp.data


def test_add_valid_workout(client):
    """Add a valid workout and confirm it's stored"""
    # Clear previous data
    for k in workouts:
        workouts[k].clear()

    data = {
        "category": "Workout",
        "exercise": "Pushups",
        "duration": "20"
    }
    resp = client.post("/add", data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert any(e["exercise"] == "Pushups" for e in workouts["Workout"])
    assert b"ACEest Fitness & Gym Tracker" in resp.data  # back to home page


def test_add_missing_fields(client):
    """Submitting with missing exercise or duration shows error"""
    data = {
        "category": "Workout",
        "exercise": "",
        "duration": "30"
    }
    resp = client.post("/add", data=data)
    assert resp.status_code == 200
    assert b"Please enter both exercise and duration" in resp.data


def test_add_invalid_duration(client):
    """Submitting non-numeric duration shows error"""
    data = {
        "category": "Workout",
        "exercise": "Squats",
        "duration": "abc"
    }
    resp = client.post("/add", data=data)
    assert resp.status_code == 200
    assert b"Duration must be a number" in resp.data


def test_summary_no_sessions(client):
    """Summary when no workouts are added"""
    # clear workouts
    for k in workouts:
        workouts[k].clear()

    resp = client.get("/summary")
    assert resp.status_code == 200
    assert b"No sessions logged yet!" in resp.data


def test_summary_with_sessions(client):
    """Summary shows workouts and correct motivational text"""
    # Add workouts manually
    workouts["Warm-up"].append({"exercise": "Jog", "duration": 10, "timestamp": "2025-11-04"})
    workouts["Workout"].append({"exercise": "Pushups", "duration": 25, "timestamp": "2025-11-04"})

    resp = client.get("/summary")
    assert resp.status_code == 200
    assert b"Jog" in resp.data
    assert b"Pushups" in resp.data
    assert b"Good start! Keep moving" in resp.data or b"Nice effort" in resp.data
