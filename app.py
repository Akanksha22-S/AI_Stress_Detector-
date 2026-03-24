from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from stress_model import predict_stress

app = Flask(__name__)
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

# ✅ CALL IT IMMEDIATELY
init_db()

# ---------------- DATABASE ---------------- #

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

        try:
            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, password)
            ).fetchone()

            conn.close()

            if user:
                return render_template("login.html", msg="Login Successful!")
            else:
                return render_template("login.html", msg="Invalid Email or Password!")

        except Exception as e:
            conn.close()
            return "<h3>Something went wrong</h3>"

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

            return render_template("login.html", msg="Signup Successful!")

        except sqlite3.IntegrityError:
            conn.close()
            return render_template("signup.html", msg="User already exists!")

        except Exception as e:
            conn.close()
            return "<h3>Something went wrong</h3>"

    return render_template("signup.html")


# ---------------- DETECTOR ---------------- #

@app.route("/detector.html")
def detector():
    return render_template("detector.html")


# ---------------- RESULT ---------------- #

@app.route("/result.html", methods=["POST"])
def result():

    try:
        accuracy = float(request.form.get("accuracy", 0))
        speed = float(request.form.get("speed", 0))
        backspaces = int(request.form.get("backspaces", 0))
    except:
        return "<h3>Error receiving data</h3>"

    # 🔹 STRESS PREDICTION
    stress = predict_stress(accuracy, speed, backspaces)

    # 🔹 CONFIDENCE SCORE
    confidence = max(0, min(100, (accuracy - backspaces * 2)))

    if stress == "No Stress":
        confidence = min(100, confidence + 10)
    elif stress == "High Stress":
        confidence = max(50, confidence)

    return render_template(
        "result.html",
        accuracy=round(accuracy, 2),
        speed=round(speed, 2),
        backspaces=backspaces,
        stress=stress,
        confidence=round(confidence, 2)
    )


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
