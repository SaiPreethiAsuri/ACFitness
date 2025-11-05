from flask import Flask, render_template, request

app = Flask(__name__)

# In-memory storage for workouts
workouts = []

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", workouts=workouts, message=None, error=None)

@app.route("/add_workout", methods=["POST"])
def add_workout():
    workout = request.form.get("workout")
    duration_str = request.form.get("duration")

    message, error = None, None

    if not workout or not duration_str:
        error = "Please enter both workout and duration."
    else:
        try:
            duration = int(duration_str)
            workouts.append({"workout": workout, "duration": duration})
            message = f"'{workout}' added successfully!"
        except ValueError:
            error = "Duration must be a number."

    return render_template("index.html", workouts=workouts, message=message, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
