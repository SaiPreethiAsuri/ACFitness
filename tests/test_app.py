import pytest
from app.app import app, workouts, CHART_DIR
import os


@pytest.fixture
def client():
    """Flask test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_workouts():
    """Ensure workouts dictionary is empty before each test"""
    for key in workouts.keys():
        workouts[key].clear()


def test_home_page_loads(client):
    """Home page should load with 200 status"""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Log Your Workout" in resp.data


def test_add_workout_valid(client):
    """Test adding a valid workout"""
    data = {"category": "Workout", "exercise": "Push-ups", "duration": "20"}
    resp = client.post("/add", data=data, follow_redirects=True)

    assert resp.status_code == 200
    assert b"Workout Summary" in resp.data
    assert len(workouts["Workout"]) == 1
    assert workouts["Workout"][0]["exercise"] == "Push-ups"


def test_add_workout_invalid_duration(client):
    """Test invalid (non-numeric) duration"""
    data = {"category": "Workout", "exercise": "Squats", "duration": "ten"}
    resp = client.post("/add", data=data)

    assert resp.status_code == 200
    assert b"Duration must be a number." in resp.data
    assert len(workouts["Workout"]) == 0


def test_add_workout_missing_fields(client):
    """Test missing exercise or duration"""
    data = {"category": "Workout", "exercise": "", "duration": ""}
    resp = client.post("/add", data=data)

    assert resp.status_code == 200
    assert b"Please enter both exercise and duration." in resp.data
    assert len(workouts["Workout"]) == 0


def test_summary_page_empty(client):
    """Summary should show zero total when no workouts"""
    resp = client.get("/summary")
    assert resp.status_code == 200
    assert b"No sessions logged yet" in resp.data


def test_summary_page_with_workouts(client):
    """Motivational message changes based on total time."""
    # Instead of workouts.clear(), reset only the session lists
    for key in workouts.keys():
        workouts[key].clear()

    # total < 30
    workouts["Workout"].append({"exercise": "Jogging", "duration": 20, "timestamp": "2025-11-04"})
    resp = client.get("/summary")
    assert b"Good start" in resp.data

    # total = 50 (< 60)
    workouts["Workout"].append({"exercise": "Push-ups", "duration": 30, "timestamp": "2025-11-04"})
    resp = client.get("/summary")
    assert b"Nice effort" in resp.data

    # total >= 60
    workouts["Workout"].append({"exercise": "Cycling", "duration": 60, "timestamp": "2025-11-04"})
    resp = client.get("/summary")
    assert b"Excellent dedication" in resp.data



def test_diet_chart_page(client):
    """Diet chart route should render diet plans"""
    resp = client.get("/diet")
    assert resp.status_code == 200
    assert b"Weight Loss" in resp.data
    assert b"Muscle Gain" in resp.data
    assert b"Endurance" in resp.data


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

