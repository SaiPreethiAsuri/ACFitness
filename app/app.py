from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os

# -------------------------------
# Safe Matplotlib Import
# -------------------------------
MATPLOTLIB_AVAILABLE = False
plt = None

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    pass

# -------------------------------
# Flask App Setup
# -------------------------------
app = Flask(__name__)

# Store workouts
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# Directory for saving charts
CHART_DIR = "static/charts"
os.makedirs(CHART_DIR, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html", workouts=workouts)


@app.route("/add", methods=["POST"])
def add_workout():
    category = request.form.get("category")
    exercise = request.form.get("exercise", "").strip()
    duration_str = request.form.get("duration", "").strip()

    if not exercise or not duration_str:
        error = "Please enter both exercise and duration."
        return render_template("index.html", workouts=workouts, error=error)

    try:
        duration = int(duration_str)
    except ValueError:
        error = "Duration must be a number."
        return render_template("index.html", workouts=workouts, error=error)

    entry = {
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)

    # Refresh charts
    generate_progress_chart()

    return redirect(url_for("summary"))


@app.route("/summary")
def summary():
    total_time = sum(entry["duration"] for sessions in workouts.values() for entry in sessions)

    if total_time == 0:
        return render_template("summary.html", workouts=workouts, total_time=0,
                               motivation="No sessions logged yet!")

    if total_time < 30:
        motivation = "Good start! Keep moving 💪"
    elif total_time < 60:
        motivation = "Nice effort! You're building consistency 🔥"
    else:
        motivation = "Excellent dedication! Keep up the great work 🏆"

    return render_template("summary.html", workouts=workouts, total_time=total_time, motivation=motivation)


@app.route("/diet")
def diet_chart():
    diet_plans = {
        "Weight Loss": ["Oatmeal with Fruits", "Grilled Chicken Salad", "Vegetable Soup", "Brown Rice & Veggies"],
        "Muscle Gain": ["Egg Omelet", "Chicken Breast", "Quinoa & Beans", "Protein Shake", "Greek Yogurt with Nuts"],
        "Endurance": ["Banana & Peanut Butter", "Whole Grain Pasta", "Sweet Potatoes", "Salmon & Avocado", "Trail Mix"]
    }
    return render_template("diet.html", diet_plans=diet_plans)


def generate_progress_chart():
    # ✅ skip processing if matplotlib is unavailable
    if not MATPLOTLIB_AVAILABLE:
        chart_path = os.path.join(CHART_DIR, "progress.png")
        if not os.path.exists(chart_path):
            with open(chart_path, "wb") as f:
                f.write(b"")  # dummy empty file
        return

    totals = {cat: sum(entry["duration"] for entry in sessions) for cat, sessions in workouts.items()}
    categories = list(totals.keys())
    values = list(totals.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    ax1.bar(categories, values, color=["#007bff", "#28a745", "#ffc107"])
    ax1.set_title("Time Spent per Category")
    ax1.set_ylabel("Minutes")

    if sum(values) > 0:
        ax2.pie(values, labels=categories, autopct="%1.1f%%", startangle=90,
                colors=["#007bff", "#28a745", "#ffc107"])
        ax2.set_title("Workout Distribution")

    plt.tight_layout()
    chart_path = os.path.join(CHART_DIR, "progress.png")
    plt.savefig(chart_path)
    plt.close(fig)




if __name__ == "__main__":
    app.run(debug=True)
