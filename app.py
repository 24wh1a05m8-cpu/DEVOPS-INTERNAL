from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import date

app = Flask(__name__)
DB = "attendance.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# Create database
def create_database():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            attendance_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Attendance System</title>

    <style>
        body {
            font-family: Arial;
            background: #f2f5f8;
            margin: 0;
        }

        header {
            background: #243b55;
            color: white;
            padding: 20px;
            text-align: center;
        }

        nav {
            margin-top: 15px;
        }

        nav a {
            color: white;
            text-decoration: none;
            margin: 15px;
        }

        .container {
            width: 90%;
            max-width: 1000px;
            margin: 30px auto;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px #ccc;
        }

        input, select {
            padding: 10px;
            margin: 5px;
        }

        button {
            padding: 10px 20px;
            background: #243b55;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
        }

        th {
            background: #243b55;
            color: white;
        }

        .present {
            color: green;
            font-weight: bold;
        }

        .absent {
            color: red;
            font-weight: bold;
        }
    </style>
</head>

<body>

<header>

    <h1>Student Attendance Management System</h1>

    <nav>
        <a href="/">Home</a>
        <a href="/add">Add Student</a>
        <a href="/mark">Mark Attendance</a>
        <a href="/records">Records</a>
    </nav>

</header>

<div class="container">

{% if page == "home" %}

    <div class="card">

        <h2>Dashboard</h2>

        <h3>Total Students: {{ total }}</h3>

        <h3>Present Today: {{ present }}</h3>

        <h3>Absent Today: {{ absent }}</h3>

    </div>

    <div class="card">

        <h2>Students</h2>

        <table>

            <tr>
                <th>Roll No</th>
                <th>Name</th>
                <th>Department</th>
                <th>Year</th>
            </tr>

            {% for s in students %}

            <tr>
                <td>{{ s.roll_no }}</td>
                <td>{{ s.name }}</td>
                <td>{{ s.department }}</td>
                <td>{{ s.year }}</td>
            </tr>

            {% endfor %}

        </table>

    </div>

{% elif page == "add" %}

    <div class="card">

        <h2>Add Student</h2>

        <form method="POST">

            <input
                type="text"
                name="name"
                placeholder="Student Name"
                required
            >

            <input
                type="text"
                name="roll"
                placeholder="Roll Number"
                required
            >

            <select name="department">

                <option>CSE</option>
                <option>ECE</option>
                <option>EEE</option>
                <option>IT</option>
                <option>AIML</option>

            </select>

            <select name="year">

                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>

            </select>

            <button type="submit">
                Add Student
            </button>

        </form>

    </div>

{% elif page == "mark" %}

    <div class="card">

        <h2>Mark Attendance</h2>

        <form method="POST">

            <p>Date: {{ today }}</p>

            <table>

                <tr>
                    <th>Roll No</th>
                    <th>Name</th>
                    <th>Attendance</th>
                </tr>

                {% for s in students %}

                <tr>

                    <td>{{ s.roll_no }}</td>

                    <td>{{ s.name }}</td>

                    <td>

                        <input
                            type="radio"
                            name="status_{{ s.id }}"
                            value="Present"
                            checked
                        >
                        Present

                        <input
                            type="radio"
                            name="status_{{ s.id }}"
                            value="Absent"
                        >
                        Absent

                    </td>

                </tr>

                {% endfor %}

            </table>

            <br>

            <button type="submit">
                Save Attendance
            </button>

        </form>

    </div>

{% elif page == "records" %}

    <div class="card">

        <h2>Attendance Records</h2>

        <table>

            <tr>
                <th>Roll No</th>
                <th>Name</th>
                <th>Date</th>
                <th>Status</th>
            </tr>

            {% for r in records %}

            <tr>

                <td>{{ r.roll_no }}</td>

                <td>{{ r.name }}</td>

                <td>{{ r.attendance_date }}</td>

                <td>

                    {% if r.status == "Present" %}

                    <span class="present">
                        Present
                    </span>

                    {% else %}

                    <span class="absent">
                        Absent
                    </span>

                    {% endif %}

                </td>

            </tr>

            {% endfor %}

        </table>

    </div>

{% endif %}

</div>

</body>
</html>
"""


@app.route("/")
def home():

    conn = db()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    today = str(date.today())

    total = len(students)

    present = conn.execute(
        """
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ?
        AND status = 'Present'
        """,
        (today,)
    ).fetchone()[0]

    absent = conn.execute(
        """
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ?
        AND status = 'Absent'
        """,
        (today,)
    ).fetchone()[0]

    conn.close()

    return render_template_string(
        HTML,
        page="home",
        students=students,
        total=total,
        present=present,
        absent=absent
    )


@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        department = request.form["department"]
        year = request.form["year"]

        conn = db()

        try:

            conn.execute(
                """
                INSERT INTO students
                (name, roll_no, department, year)
                VALUES (?, ?, ?, ?)
                """,
                (name, roll, department, year)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Roll number already exists!"

        conn.close()

        return redirect("/")

    return render_template_string(
        HTML,
        page="add"
    )


@app.route("/mark", methods=["GET", "POST"])
def mark_attendance():

    conn = db()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    if request.method == "POST":

        today = str(date.today())

        for student in students:

            status = request.form.get(
                "status_" + str(student["id"]),
                "Absent"
            )

            conn.execute(
                """
                INSERT INTO attendance
                (student_id, attendance_date, status)
                VALUES (?, ?, ?)
                """,
                (
                    student["id"],
                    today,
                    status
                )
            )

        conn.commit()

        conn.close()

        return redirect("/records")

    conn.close()

    return render_template_string(
        HTML,
        page="mark",
        students=students,
        today=date.today()
    )


@app.route("/records")
def records():

    conn = db()

    records = conn.execute(
        """
        SELECT
            students.roll_no,
            students.name,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template_string(
        HTML,
        page="records",
        records=records
    )


@app.route("/health")
def health():

    return {
        "status": "Running",
        "project": "Student Attendance Management System"
    }


if __name__ == "__main__":

    create_database()

    print("Student Attendance System Started!")
    print("Open: http://127.0.0.1:5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )