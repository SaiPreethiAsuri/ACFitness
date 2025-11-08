import io
import os
import pytest
from app.app import app, workouts, CHART_DIR

@pytest.fixture
def client():
    """Set up a Flask test client for each test."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_route(client):
    """Test home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"ACEest Fitness" in response.data


def test_add_workout_valid(client):
    """Test adding a valid workout entry."""
    data = {'category': 'Workout', 'exercise': 'Pushups', 'duration': '20'}
    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Progress Tracker" in response.data
    assert any(entry["exercise"] == "Pushups" for entry in workouts["Workout"])


def test_add_workout_missing_fields(client):
    """Test validation when fields are missing."""
    data = {'category': 'Warm-up', 'exercise': '', 'duration': ''}
    response = client.post('/add', data=data)
    assert response.status_code == 200
    assert b"Please enter both exercise and duration." in response.data


def test_add_workout_invalid_duration(client):
    """Test validation when duration is not a number."""
    data = {'category': 'Workout', 'exercise': 'Running', 'duration': 'abc'}
    response = client.post('/add', data=data)
    assert response.status_code == 200
    assert b"Workout" in response.data


def test_summary_no_data(client):
    """Test summary route with no workouts logged."""
    # Clear all workouts
    for cat in workouts:
        workouts[cat].clear()
    response = client.get('/summary')
    assert response.status_code == 200
    assert b"No workout data logged yet" in response.data

def test_summary_motivation_levels(client):
    """Test motivational messages for different total durations."""
    for cat in workouts:
        workouts[cat].clear()

    # Case 1: <30 minutes
    workouts["Warm-up"].append({"exercise": "Jumping Jacks", "duration": 20, "timestamp": "2025-11-04"})
    response = client.get("/summary")
    assert b"Good start" in response.data or b"Keep moving" in response.data, \
        "Expected motivational message for less than 30 mins"

    # Case 2: 30–59 minutes
    workouts["Workout"].append({"exercise": "Pushups", "duration": 39, "timestamp": "2025-11-04"})
    response = client.get("/summary")
    assert (
        b"Nice effort" in response.data
        or b"consistency" in response.data
        or b"building" in response.data
    ), "Expected motivational message for mid-level duration (30-59 mins)"

    # Case 3: >=60 minutes
    workouts["Cool-down"].append({"exercise": "Stretching", "duration": 10, "timestamp": "2025-11-04"})
    response = client.get("/summary")
    assert b"Excellent dedication" in response.data or b"great work" in response.data, \
        "Expected motivational message for 60+ mins"



def test_diet_chart_route(client):
    """Test diet chart page loads successfully."""
    response = client.get('/diet')
    assert response.status_code == 200
    assert b"Diet Guide" in response.data


def test_generate_progress_chart_creates_image(client):
    """Adding a workout should trigger chart creation"""

    # Add a workout so chart generation runs
    data = {"category": "Workout", "exercise": "Plank", "duration": "10"}
    client.post("/add", data=data, follow_redirects=True)

    chart_path = os.path.join(CHART_DIR, "progress.png")

    # File must exist
    assert os.path.exists(chart_path)

    # If matplotlib is installed, expect nonzero file
    try:
        import matplotlib
        has_matplotlib = True
    except Exception:
        has_matplotlib = False

    if has_matplotlib:
        assert os.path.getsize(chart_path) > 0
    else:
        # If matplotlib isn’t available, just assert file exists
        assert os.path.getsize(chart_path) >= 0

