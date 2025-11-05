import pytest
from app import app, workouts

@pytest.fixture
def client():
    # Set up a test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Clear workouts before each test
        workouts.clear()
        yield client

def test_home_page_loads(client):
    """Test that the home page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEestFitness and Gym" in response.data
    assert b"No workouts logged yet." in response.data

def test_add_valid_workout(client):
    """Test adding a valid workout"""
    response = client.post("/add_workout", data={
        "workout": "Pushups",
        "duration": "30"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Pushups" in response.data
    assert b"added successfully" in response.data
    assert len(workouts) == 1
    assert workouts[0]["workout"] == "Pushups"
    assert workouts[0]["duration"] == 30

def test_add_workout_missing_fields(client):
    """Test that missing fields show an error"""
    response = client.post("/add_workout", data={
        "workout": "",
        "duration": "20"
    })
    assert b"Please enter both workout and duration." in response.data
    assert len(workouts) == 0

def test_add_workout_invalid_duration(client):
    """Test that non-numeric duration shows an error"""
    response = client.post("/add_workout", data={
        "workout": "Situps",
        "duration": "abc"
    })
    assert b"Duration must be a number." in response.data
    assert len(workouts) == 0

def test_workouts_persist_in_memory(client):
    """Test that workouts persist during a single test session"""
    client.post("/add_workout", data={"workout": "Plank", "duration": "10"})
    response = client.get("/")
    assert b"Plank - 10 minutes" in response.data
    assert len(workouts) == 1
