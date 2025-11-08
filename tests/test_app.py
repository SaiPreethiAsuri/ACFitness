import pytest
from app.app import app, workouts

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Ensure home (log workout) page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Warm-up" in response.data or b"Workout" in response.data


def test_add_valid_workout(client):
    """Add a valid workout and verify it's stored."""
    for w in workouts.values():
        w.clear()

    data = {
        "category": "Workout",
        "exercise": "Pushups",
        "duration": "20"
    }
    response = client.post("/", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert any("Pushups" in e["exercise"] for e in workouts["Workout"])


def test_add_invalid_workout_missing_fields(client):
    """Test adding invalid workout (empty fields)."""
    response = client.post("/", data={"category": "Workout", "exercise": "", "duration": ""}, follow_redirects=True)
    assert b"Please enter both exercise and duration" in response.data


def test_add_invalid_workout_negative_duration(client):
    """Test adding invalid workout (negative duration)."""
    response = client.post("/", data={"category": "Warm-up", "exercise": "Jogging", "duration": "-5"}, follow_redirects=True)
    assert b"Duration must be a positive whole number" in response.data


def test_progress_no_data(client):
    """Progress page with no data."""
    for w in workouts.values():
        w.clear()
    response = client.get("/progress")
    assert response.status_code == 200
    assert b"No workout data" not in response.data  # Should not break


def test_progress_with_data(client):
    """Progress page generates chart when data exists."""
    for w in workouts.values():
        w.clear()
    workouts["Warm-up"].append({"exercise": "Jumping Jacks", "duration": 10, "timestamp": "2025-11-04"})
    workouts["Workout"].append({"exercise": "Pushups", "duration": 30, "timestamp": "2025-11-04"})
    workouts["Cool-down"].append({"exercise": "Stretching", "duration": 5, "timestamp": "2025-11-04"})

    response = client.get("/progress")
    assert response.status_code == 200
    assert b"charts/progress.png" in response.data


def test_plan_and_diet_pages(client):
    """Ensure plan and diet pages load correctly."""
    response_plan = client.get("/plan")
    response_diet = client.get("/diet")

    assert response_plan.status_code == 200
    assert b"Warm-up" in response_plan.data or b"Cardio" in response_plan.data

    assert response_diet.status_code == 200
    assert b"Weight Loss" in response_diet.data or b"Protein" in response_diet.data
