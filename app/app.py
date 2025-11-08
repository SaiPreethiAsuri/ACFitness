from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from datetime import datetime, date
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from datetime import datetime, date
import os
import io

# -------------------------------
# SAFE MATPLOTLIB IMPORT
# -------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    plt = None
    MATPLOTLIB_AVAILABLE = False

# -------------------------------
# SAFE REPORTLAB IMPORT
# -------------------------------
try:
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors as rl_colors
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "fitness_secret"

# ---------- Data ---------- #
user_info = {}
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

# ---------- MET Values ---------- #
MET_VALUES = {
    "Warm-up": 3,
    "Workout": 6,
    "Cool-down": 2.5
}


# ---------- HOME PAGE (User Info + Workout Logger) ---------- #
@app.route("/", methods=["GET", "POST"])
def home():
    global user_info

    if request.method == "POST":
        name = request.form.get("name")
        regn_id = request.form.get("regn_id")
        age_val = request.form.get("age")
        gender = request.form.get("gender")
        height_val = request.form.get("height")
        weight_val = request.form.get("weight")

        # ✅ Validation before casting
        if not all([name, regn_id, age_val, gender, height_val, weight_val]):
            return "Missing required fields", 400

        try:
            age = int(age_val)
            height = float(height_val)
            weight = float(weight_val)
        except ValueError:
            return "Invalid numeric input", 400

        gender = gender.upper()
        user_info = {
            "name": name,
            "regn_id": regn_id,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
        }

        return redirect("/plan")

    return render_template("index.html")



# ---------- ADD WORKOUT ---------- #
@app.route("/add", methods=["POST"])
def add_workout():
    category = request.form.get("category")
    exercise = request.form.get("exercise")
    duration_str = request.form.get("duration")

    if not exercise or not duration_str:
        flash("Please enter both exercise and duration.", "error")
        return redirect(url_for("home"))

    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError
    except ValueError:
        flash("Duration must be a positive number.", "error")
        return redirect(url_for("home"))

    weight = user_info.get("weight", 70)
    met = MET_VALUES.get(category, 5)
    calories = (met * 3.5 * weight / 200) * duration
    entry = {
        "exercise": exercise,
        "duration": duration,
        "calories": calories,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts[category].append(entry)
    flash(f"Added {exercise} ({duration} min) to {category}! 💪", "success")
    return redirect(url_for("home"))


# ---------- SUMMARY PAGE ---------- #
@app.route("/summary")
def summary():
    total_time = sum(sum(e["duration"] for e in w) for w in workouts.values())
    return render_template("summary.html", workouts=workouts, total_time=total_time)


# ---------- PROGRESS CHART ---------- #
@app.route("/progress")
def progress():
    totals = {cat: sum(e["duration"] for e in sessions) for cat, sessions in workouts.items()}
    total_minutes = sum(totals.values())

    if total_minutes == 0:
        return render_template("progress.html", total_minutes=0)

    # Create charts folder
    os.makedirs("static/charts", exist_ok=True)
    chart_path = os.path.join("static", "charts", "progress.png")

    # ------- Fallback if matplotlib missing -------
    if not MATPLOTLIB_AVAILABLE:
        with open(chart_path, "wb") as f:
            f.write(b"")  # empty placeholder file
        return render_template("progress.html", total_minutes=total_minutes, chart_file="charts/progress.png")

    # ------- Normal matplotlib chart generation -------
    labels = list(totals.keys())
    values = list(totals.values())
    colors = ["#2196F3", "#4CAF50", "#FFC107"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    ax1.bar(labels, values, color=colors)
    ax1.set_title("Total Minutes per Category")
    ax1.set_ylabel("Minutes")

    filtered_labels = [l for l, v in zip(labels, values) if v > 0]
    filtered_values = [v for v in values if v > 0]
    filtered_colors = [c for c, v in zip(colors, values) if v > 0]

    ax2.pie(filtered_values, labels=filtered_labels, autopct="%1.1f%%",
            startangle=90, colors=filtered_colors)
    ax2.set_title("Workout Distribution (%)")

    plt.tight_layout()
    plt.savefig(chart_path, transparent=True)
    plt.close(fig)

    return render_template("progress.html", total_minutes=total_minutes, chart_file="charts/progress.png")



# ---------- PDF EXPORT ---------- #
@app.route("/export")
def export_pdf():
    if not user_info:
        flash("Please save user info first!", "error")
        return redirect(url_for("home"))

    # ------- Fallback if reportlab missing -------
    if not REPORTLAB_AVAILABLE:
        return "PDF unavailable. ReportLab is not installed.", 200

    # ------- Normal PDF generation -------
    filename = f"{user_info['name'].replace(' ', '_')}_weekly_report.pdf"
    c = pdf_canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Weekly Fitness Report - {user_info['name']}")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80,
                 f"Regn-ID: {user_info['regn_id']} | Age: {user_info['age']} | Gender: {user_info['gender']}")

    # Handle missing BMI/BMR
    bmi = user_info.get("bmi", 0)
    bmr = user_info.get("bmr", 0)

    c.drawString(50, height - 100,
                 f"Height: {user_info['height']} cm | Weight: {user_info['weight']} kg | "
                 f"BMI: {bmi:.1f} | BMR: {bmr:.0f} kcal/day")

    # Table data
    y = height - 140
    table_data = [["Category", "Exercise", "Duration(min)", "Calories(kcal)", "Date"]]
    for cat, sessions in workouts.items():
        for e in sessions:
            table_data.append([
                cat, e['exercise'], str(e['duration']),
                f"{e['calories']:.1f}", e['timestamp'].split()[0]
            ])

    table = Table(table_data, colWidths=[80, 150, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.black)
    ]))
    table.wrapOn(c, width - 100, y)
    table.drawOn(c, 50, y - 20)
    c.save()

    return send_file(filename, as_attachment=True)



# ---------- RUN APP ---------- #
if __name__ == "__main__":
    app.run(debug=True)
