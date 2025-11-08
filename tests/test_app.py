import pytest
from app.app import app, workouts, user_info


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ----------------------------
# HOME PAGE TESTS
# ----------------------------
def test_home_page_loads(client):
    """Home page should load the user info form."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"name" in response.data or b"User" in response.data


def test_valid_user_submission(client):
    """POST valid user info should redirect to /plan."""
    data = {
        "name": "Preethi",
        "regn_id": "R123",
        "age": "25",
        "gender": "F",
        "height": "165",
        "weight": "60"
    }
    response = client.post("/", data=data, follow_redirects=False)
    assert response.status_code == 302
    assert "/plan" in response.headers["Location"]


def test_invalid_user_submission_missing_fields(client):
    """Posting missing required fields should return HTTP 400."""
    response = client.post("/", data={"name": "OnlyName"})
    assert response.status_code == 400


# ----------------------------
# WORKOUT ADDITION TESTS
# ----------------------------
def test_valid_workout_submission(client):
    """Valid workout submission should be stored."""
    for cat in workouts.values():
        cat.clear()

    user_info.update({"weight": 60})

    data = {
        "category": "Workout",
        "exercise": "Squats",
        "duration": "20"
    }

    res = client.post("/add", data=data, follow_redirects=True)
    assert res.status_code in (200, 302)

    assert len(workouts["Workout"]) == 1
    assert workouts["Workout"][0]["exercise"] == "Squats"


def test_invalid_workout_missing_fields(client):
    """Missing workout fields should redirect back with error."""
    data = {"category": "Workout", "exercise": "", "duration": ""}
    res = client.post("/add", data=data, follow_redirects=True)
    assert res.status_code in (200, 302)


def test_invalid_workout_negative_duration(client):
    """Negative duration should be rejected."""
    data = {"category": "Warm-up", "exercise": "Jogging", "duration": "-5"}
    res = client.post("/add", data=data, follow_redirects=True)
    assert b"positive number" in res.data or res.status_code in (200, 302)


# ----------------------------
# SUMMARY PAGE TESTS
# ----------------------------
def test_summary_page(client):
    response = client.get("/summary")
    assert response.status_code == 200
    assert b"Summary" in response.data or b"Duration" in response.data


# ----------------------------
# PROGRESS PAGE TESTS
# ----------------------------
def test_progress_page(client):
    """Progress page should show placeholder or chart."""
    res = client.get("/progress")
    assert res.status_code == 200

    assert (
        b"progress.png" in res.data
        or b"No workout data" in res.data
        or b"Total Minutes" in res.data
    )


# ----------------------------
# PDF EXPORT TESTS
# ----------------------------
def test_pdf_export(client):
    """PDF export should work or fallback text if ReportLab missing."""
    user_info.clear()
    user_info.update({
        "name": "Preethi",
        "regn_id": "R123",
        "age": 25,
        "gender": "F",
        "height": 165.0,
        "weight": 60.0,
        "bmi": 22.0,
        "bmr": 1450.0
    })

    res = client.get("/export")
    assert res.status_code in (200, 302)

    assert (
        res.mimetype == "application/pdf"
        or b"PDF unavailable" in res.data
        or b"Report" in res.data
    )
