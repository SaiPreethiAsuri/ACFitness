from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Store workouts in memory
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}


@app.route('/')
def index():
    """Render main tabbed interface"""
    return render_template('index.html', workouts=workouts)


@app.route('/add', methods=['POST'])
def add_workout():
    """Add workout from form submission"""
    category = request.form.get('category')
    exercise = request.form.get('exercise', '').strip()
    duration_str = request.form.get('duration', '').strip()

    if not exercise or not duration_str:
        return render_template('index.html', workouts=workouts, error="Please enter both exercise and duration.")

    try:
        duration = int(duration_str)
    except ValueError:
        return render_template('index.html', workouts=workouts, error="Duration must be a number.")

    entry = {
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)
    return redirect(url_for('index'))


@app.route('/summary')
def summary():
    """Return summary data for modal or embedded tab"""
    total_time = sum(entry['duration'] for sessions in workouts.values() for entry in sessions)

    if total_time == 0:
        motivation = "No sessions logged yet!"
    elif total_time < 30:
        motivation = "Good start! Keep moving 💪"
    elif total_time < 60:
        motivation = "Nice effort! You're building consistency 🔥"
    else:
        motivation = "Excellent dedication! Keep up the great work 🏆"

    return render_template('index.html', workouts=workouts, total_time=total_time, motivation=motivation)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
