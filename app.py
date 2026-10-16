from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret-key"

DB = Path(__file__).resolve().parent / "students.db"

COURSES = ["Python", "Java", "Web Development", "Data Science", "AI & ML"]


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            course TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        age_text = request.form.get("age", "")
        gender = request.form.get("gender", "")
        course = request.form.get("course", "")
        password = request.form.get("password", "")

        if not all([name, email, age_text, gender, course, password]):
            return render_template("register.html",
                                   error="All fields are required.")

        try:
            age = int(age_text)
            if age <= 0 or len(password) < 6:
                raise ValueError
            if course not in COURSES:
                raise ValueError
            if gender not in ["Male", "Female", "Other"]:
                raise ValueError
        except ValueError:
            return render_template(
                "register.html",
                error="Enter valid details and a password of 6+ characters."
            )

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO students (name, email, age, gender, course, password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, email, age, gender, course,
                  generate_password_hash(password)))
            conn.commit()
            return redirect(url_for("success", name=name))
        except sqlite3.IntegrityError:
            return render_template(
                "register.html", error="Email is already registered."
            )
        except sqlite3.Error:
            return render_template(
                "register.html", error="Database error. Please try again."
            )
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/success")
def success():
    name = request.args.get("name", "Student")
    return render_template("success.html", name=name)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        student = conn.execute(
            "SELECT * FROM students WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if student and check_password_hash(student["password"], password):
            session.clear()
            session["student_id"] = student["id"]
            return redirect(url_for("profile"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/profile")
def profile():
    student_id = session.get("student_id")

    if not student_id:
        return redirect(url_for("login"))

    conn = get_db()
    student = conn.execute(
        "SELECT id, name, email, age, gender, course "
        "FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()

    if not student:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html", student=student, courses=COURSES
    )


@app.route("/update-course", methods=["POST"])
def update_course():
    student_id = session.get("student_id")

    if not student_id:
        return jsonify(success=False, message="Please log in again."), 401

    course = request.form.get("course", "")

    if course not in COURSES:
        return jsonify(success=False, message="Invalid course."), 400

    conn = get_db()
    try:
        result = conn.execute(
            "UPDATE students SET course = ? WHERE id = ?",
            (course, student_id)
        )
        conn.commit()

        if result.rowcount == 0:
            return jsonify(success=False, message="Student not found."), 404

        return jsonify(success=True, course=course)
    except sqlite3.Error:
        conn.rollback()
        return jsonify(success=False, message="Database update failed."), 500
    finally:
        conn.close()


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
