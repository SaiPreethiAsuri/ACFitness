from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    matplotlib = None
    plt = None
# -------------------------------
# Flask App Setup
# -------------------------------
import os
import io
import base64

app = Flask(__name__)

# Store workouts
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# Directory for saving charts
CHART_DIR = "static/charts"
os.makedirs(CHART_DIR, exist_ok=True)

@app.route("/")
def home():
    """Landing page with all tabs"""
    return render_template("index.html", workouts=workouts)

@app.route("/add", methods=["POST"])
def add_workout():
    """Add a workout session"""
    category = request.form.get("category")
    exercise = request.form.get("exercise", "").strip()
    duration_str = request.form.get("duration", "").strip()

    if not exercise or not duration_str:
        error = "Please enter both exercise and duration."
        return render_template("index.html", workouts=workouts, error=error)

    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError
    except ValueError:
        error = "Duration must be a positive number."
        return render_template("index.html", workouts=workouts, error=error)

    entry = {
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)

    generate_progress_chart()

    return redirect(url_for("progress"))

@app.route("/summary")
def summary():
    total_time = sum(entry["duration"] for sessions in workouts.values() for entry in sessions)

    if total_time == 0:
        return render_template("summary.html", workouts=workouts, total_time=0,
                               motivation="No sessions logged yet!", plot_url=None)

    # Motivational message
    if total_time < 30:
        motivation = "Good start! Keep moving"
    elif total_time < 60:
        motivation = "Nice effort! You are building consistency"
    else:
        motivation = "Excellent dedication! Keep up the great work"

    # ✅ If matplotlib is NOT installed, skip chart creation
    if plt is None:
        return render_template(
            "summary.html",
            workouts=workouts,
            total_time=total_time,
            motivation=motivation,
            plot_url=None
        )

    # ✅ Otherwise, generate pie chart
    labels = list(workouts.keys())
    times = [sum(entry["duration"] for entry in sessions) for sessions in workouts.values()]

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(times, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    # Convert chart to base64
    import io, base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template(
        "summary.html",
        workouts=workouts,
        total_time=total_time,
        motivation=motivation,
        plot_url=plot_url
    )



@app.route("/diet")
def diet_chart():
    """Diet guide page"""
    diet_plans = {
        "Weight Loss": ["Oatmeal with Berries", "Grilled Chicken Salad", "Vegetable Soup with Lentils"],
        "Muscle Gain": ["3 Egg Omelet with Spinach", "Chicken Breast, Quinoa, Veggies", "Protein Shake & Yogurt"],
        "Endurance": ["Banana & Peanut Butter", "Whole Grain Pasta", "Salmon & Avocado Salad"]
    }
    return render_template("diet.html", diet_plans=diet_plans)

@app.route("/progress")
def progress():
    """Progress chart page"""
    generate_progress_chart()
    total_time = sum(entry["duration"] for sessions in workouts.values() for entry in sessions)
    return render_template("progress.html", total_time=total_time)

def generate_progress_chart():
    if plt is None:
        return  # Skip charting safely

    totals = {cat: sum(entry['duration'] for entry in sessions) for cat, sessions in workouts.items()}

    categories = list(totals.keys())
    values = list(totals.values())

    categories_nonzero = [cat for cat, val in zip(categories, values) if val > 0]
    values_nonzero = [val for val in values if val > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    fig.subplots_adjust(wspace=0.4)

    ax1.bar(categories, values, color=["#007bff", "#28a745", "#ffc107"])
    ax1.set_title("⏱ Time Spent per Category")

    # pie only if data exists
    if sum(values_nonzero) > 0:
        ax2.pie(values_nonzero, labels=categories_nonzero)
    else:
        ax2.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax2.axis("off")

    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, "progress.png"))
    plt.close(fig)

if __name__ == "__main__":
    app.run(debug=True)
