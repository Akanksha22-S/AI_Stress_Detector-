from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from stress_model import predict_stress

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DB INIT ---------------- #
def init_db():
    if not os.path.exists("database.db"):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, 
            email TEXT UNIQUE,
            password TEXT
        )
        """)

        conn.commit()
        conn.close()

init_db()


# ---------------- DB ---------------- #
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return render_template("main.html")


# ---------------- ABOUT ---------------- #
@app.route("/about.html")
def about():
    return render_template("about.html")


# ---------------- LOGIN ---------------- #
@app.route("/login.html", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = email
            session["trial_used"] = False
            return redirect(url_for("detector"))
        else:
            return render_template("login.html", msg="Invalid Email or Password!")

    return render_template("login.html")


# ---------------- SIGNUP ---------------- #
@app.route("/signup.html", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            conn.close()

            session["user"] = email
            session["trial_used"] = False

            return redirect(url_for("detector"))

        except sqlite3.IntegrityError:
            conn.close()
            return render_template("signup.html", msg="User already exists!")

    return render_template("signup.html")


# ---------------- DETECTOR ---------------- #
@app.route("/detector.html")
def detector():

    if "user" not in session:
        if session.get("trial_used"):
            return redirect(url_for("login"))

    return render_template("detector.html")


# ---------------- CHECK LOGIN ---------------- #
@app.route("/check_login")
def check_login():
    return {"logged_in": "user" in session}


# ---------------- RESULT ---------------- #
@app.route("/result.html", methods=["POST"])
def result():

    accuracy = float(request.form.get("accuracy", 0))
    speed = float(request.form.get("speed", 0))
    backspaces = int(request.form.get("backspaces", 0))

    stress = predict_stress(accuracy, speed, backspaces)

    # MARK TRIAL ONLY FOR GUEST
    if "user" not in session:
        session["trial_used"] = True

    confidence = max(0, min(100, (accuracy - backspaces * 2)))

    return render_template(
        "result.html",
        accuracy=round(accuracy, 2),
        speed=round(speed, 2),
        backspaces=backspaces,
        stress=stress,
        confidence=round(confidence, 2)
    )


# ---------------- VIEW USERS (NEW - FOR DEPLOYED DB) ---------------- #
@app.route("/view_db")
def view_db():

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return render_template("view_db.html", users=users)


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
