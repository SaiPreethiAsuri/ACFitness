from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Initialize categorized workout storage
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}


@app.route("/")
def home():
    """Render home page with form to add a session"""
    return render_template("index.html", workouts=workouts, message=None, error=None)


@app.route("/add_workout", methods=["POST"])
def add_workout():
    """Handle workout submission"""
    category = request.form.get("category")
    workout = request.form.get("workout", "").strip()
    duration_str = request.form.get("duration", "").strip()
    message, error = None, None

    if not workout or not duration_str:
        error = "Please enter both exercise and duration."
    else:
        try:
            duration = int(duration_str)
            entry = {
                "exercise": workout,
                "duration": duration,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            workouts[category].append(entry)
            message = f"{workout} added to {category} category successfully!"
        except ValueError:
            error = "Duration must be a number."

    return render_template("index.html", workouts=workouts, message=message, error=error)


@app.route("/summary")
def view_summary():
    """Display categorized summary of workouts"""
    total_time = sum(entry["duration"] for sessions in workouts.values() for entry in sessions)

    if total_time == 0:
        return render_template("summary.html", workouts=workouts, total_time=0, motivation="No sessions logged yet!")

    # Motivational message logic
    if total_time < 30:
        motivation = "Good start! Keep moving"
    elif total_time < 60:
        motivation = "Nice effort! You're building consistency"
    else:
        motivation = "Excellent dedication! Keep up the great work"

    return render_template("summary.html", workouts=workouts, total_time=total_time, motivation=motivation)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
