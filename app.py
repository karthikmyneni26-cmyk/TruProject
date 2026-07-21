from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "tru-projects-secret-key-change-this"
DATABASE = "tru_projects.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT,
            message TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            college TEXT,
            course TEXT,
            branch TEXT,
            service TEXT,
            message TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/research")
def research():
    return render_template("research.html")

@app.route("/documents")
def documents():
    return render_template("documents.html")

@app.route("/internships")
def internships():
    return render_template("internships.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        service = request.form.get("service", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not phone or not email or not message:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("contact"))

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO enquiries
            (name, phone, email, service, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, email, service, message,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        flash("Thank you! Your enquiry has been submitted successfully.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        college = request.form.get("college", "").strip()
        course = request.form.get("course", "").strip()
        branch = request.form.get("branch", "").strip()
        service = request.form.get("service", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not phone or not email or not message:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("register"))

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO registrations
            (name, phone, email, college, course, branch, service, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, email, college, course, branch, service, message,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        flash("Registration submitted successfully! Our team will contact you soon.", "success")
        return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/admin")
def admin():
    conn = get_db_connection()
    enquiries = conn.execute("SELECT * FROM enquiries ORDER BY id DESC").fetchall()
    registrations = conn.execute("SELECT * FROM registrations ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", enquiries=enquiries, registrations=registrations)

@app.route("/admin/delete-enquiry/<int:id>")
def delete_enquiry(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM enquiries WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Enquiry deleted successfully.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/delete-registration/<int:id>")
def delete_registration(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM registrations WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Registration deleted successfully.", "success")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

    from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("tru_projects.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/admin/history")
def admin_history():

    conn = get_db_connection()

    # Total registered users
    total_users = conn.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    # Average rating
    average_rating = conn.execute(
        "SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL"
    ).fetchone()[0]

    if average_rating is None:
        average_rating = 0

    # Total feedback
    total_feedback = conn.execute(
        "SELECT COUNT(*) FROM feedback"
    ).fetchone()[0]

    # Individual user ratings
    user_ratings = conn.execute("""
        SELECT
            name,
            email,
            rating,
            comment,
            created_at
        FROM feedback
        ORDER BY created_at DESC
    """).fetchall()

    # Recent registrations
    recent_users = conn.execute("""
        SELECT
            name,
            email,
            phone,
            service,
            created_at
        FROM registrations
        ORDER BY created_at DESC
        LIMIT 10
    """).fetchall()

    # Rating distribution
    rating_distribution = []

    for rating in range(1, 6):

        count = conn.execute(
            "SELECT COUNT(*) FROM feedback WHERE rating = ?",
            (rating,)
        ).fetchone()[0]

        rating_distribution.append({
            "rating": rating,
            "count": count
        })

    conn.close()

    return render_template(
        "admin_history.html",
        total_users=total_users,
        average_rating=round(average_rating, 1),
        total_feedback=total_feedback,
        user_ratings=user_ratings,
        recent_users=recent_users,
        rating_distribution=rating_distribution
    )
