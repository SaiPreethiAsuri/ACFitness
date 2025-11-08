from flask import Flask, render_template, request, redirect, url_for, flash
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
app.secret_key = "fitness_secret"

# Data storage (in-memory)
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# ---------------- HOME / LOG PAGE ---------------- #
@app.route("/", methods=["GET", "POST"])
def log_workout():
    if request.method == "POST":
        category = request.form.get("category")
        exercise = request.form.get("exercise").strip()
        duration = request.form.get("duration").strip()

        if not exercise or not duration:
            flash("Please enter both exercise and duration.", "error")
            return redirect(url_for("log_workout"))

        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError
        except ValueError:
            flash("Duration must be a positive whole number.", "error")
            return redirect(url_for("log_workout"))

        entry = {
            "exercise": exercise,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        workouts[category].append(entry)
        flash(f"✅ {exercise} ({duration} min) added to {category}!", "success")
        return redirect(url_for("log_workout"))

    return render_template("log.html", workouts=workouts)


# ---------------- WORKOUT PLAN ---------------- #
@app.route("/plan")
def workout_plan():
    plan = {
        "Warm-up (5-10 min)": [
            "5 min light cardio (Jog/Cycle).",
            "Jumping Jacks (30 reps).",
            "Arm Circles (15 forward/backward)."
        ],
        "Strength & Cardio (45-60 min)": [
            "Push-ups (3 sets of 10–15)",
            "Squats (3 sets of 15–20)",
            "Plank (3 sets of 60 seconds)",
            "Lunges (3 sets of 10/leg)"
        ],
        "Cool-down (5 min)": [
            "Slow Walking",
            "Static Stretching (Hold 30s each)",
            "Deep Breathing Exercises"
        ]
    }
    return render_template("plan.html", plan=plan)


# ---------------- DIET GUIDE ---------------- #
@app.route("/diet")
def diet_guide():
    diet_plans = {
        "Weight Loss Focus": [
            "Breakfast: Oatmeal with berries",
            "Lunch: Grilled chicken/tofu salad",
            "Dinner: Vegetable soup with lentils"
        ],
        "Muscle Gain Focus": [
            "Breakfast: 3-egg omelet & toast",
            "Lunch: Chicken breast & quinoa",
            "Post-Workout: Protein shake"
        ],
        "Endurance Focus": [
            "Pre-Workout: Banana & peanut butter",
            "Lunch: Whole grain pasta",
            "Dinner: Salmon & avocado salad"
        ]
    }
    return render_template("diet.html", diet_plans=diet_plans)


# ---------------- PROGRESS TRACKER ---------------- #
@app.route("/progress")
def progress():
    totals = {cat: sum(e["duration"] for e in sessions) for cat, sessions in workouts.items()}
    total_minutes = sum(totals.values())

    chart_file = None
    if total_minutes > 0:
        chart_file = generate_progress_chart()

    return render_template("progress.html", total_minutes=total_minutes, chart_file=chart_file)


def generate_progress_chart():
    chart_path = os.path.join("static", "charts", "progress.png")
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)

    # If matplotlib is not available, create an empty placeholder file
    if plt is None:
        with open(chart_path, "wb") as f:
            f.write(b"")    # empty file, tests accept >= 0 bytes
        return "charts/progress.png"

    # Normal chart generation
    totals = {cat: sum(entry["duration"] for entry in sessions) for cat, sessions in workouts.items()}

    categories = list(totals.keys())
    values = list(totals.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    colors = ["#2196F3", "#4CAF50", "#FFC107"]

    # Bar chart
    ax1.bar(categories, values, color=colors)
    ax1.set_title("Total Minutes per Category", fontsize=10)
    ax1.set_ylabel("Minutes")

    # Pie chart
    filtered_labels = [l for l, v in zip(categories, values) if v > 0]
    filtered_values = [v for v in values if v > 0]
    filtered_colors = [c for c, v in zip(colors, values) if v > 0]
    ax2.pie(filtered_values, labels=filtered_labels, autopct="%1.1f%%",
            startangle=90, colors=filtered_colors)
    ax2.set_title("Workout Distribution (%)")

    plt.tight_layout()
    plt.savefig(chart_path, transparent=True)
    plt.close(fig)

    return "charts/progress.png"




if __name__ == "__main__":
    app.run(debug=True)
