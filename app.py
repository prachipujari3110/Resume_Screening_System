import os
import re
import random
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pypdf import PdfReader

from ml_engine import predict_resume

from config import SECRET_KEY, UPLOAD_RESUMES, UPLOAD_PHOTOS
from database import get_connection

app = Flask(__name__)
app.secret_key = SECRET_KEY

os.makedirs(UPLOAD_RESUMES, exist_ok=True)
os.makedirs(UPLOAD_PHOTOS, exist_ok=True)

SKILLS = [
    "python", "java", "sql", "mysql", "flask", "django",
    "html", "css", "javascript", "react", "pandas", "numpy",
    "machine learning", "scikit-learn", "tensorflow", "keras",
    "excel", "git", "c", "c++"
]


def current_user():
    if not session.get("user_id"):
        return None

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user


@app.context_processor
def common_data():
    user = current_user()
    notification_count = 0

    if user:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM notifications "
            "WHERE user_id=%s AND is_read=0",
            (user["id"],)
        )
        notification_count = cursor.fetchone()[0]
        cursor.close()
        connection.close()

    return {
        "current_name": user["full_name"] if user else "",
        "notification_count": notification_count
    }


def login_required():
    return bool(session.get("user_id"))


def admin_required():
    return session.get("role") == "admin"


def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return " ".join(pages)
    except Exception:
        return ""


def detect_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    return found


def get_job(job_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs WHERE id=%s", (job_id,))
    job = cursor.fetchone()
    cursor.close()
    connection.close()
    return job


def add_audit(action, details):
    if not session.get("user_id"):
        return

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO audit_logs(admin_id, action, details) VALUES(%s,%s,%s)",
        (session["user_id"], action, details)
    )
    connection.commit()
    cursor.close()
    connection.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile = request.form.get("mobile", "").strip()
        qualification = request.form.get("qualification", "").strip()
        experience = request.form.get("experience", "").strip()
        location = request.form.get("location", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users "
                "(full_name,email,mobile,password_hash,qualification,"
                "experience,location,role,email_verified) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,'candidate',1)",
                (
                    full_name,
                    email,
                    mobile,
                    generate_password_hash(password),
                    qualification,
                    experience,
                    location
                )
            )
            connection.commit()
            flash("Registration successful. You can login now.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            connection.rollback()
            flash("Registration failed. Email may already exist.", "danger")
        finally:
            cursor.close()
            connection.close()

    return render_template("auth/register.html")


@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("admin_register"))

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users "
                "(full_name,email,password_hash,role,email_verified) "
                "VALUES(%s,%s,%s,'admin',1)",
                (
                    full_name,
                    email,
                    generate_password_hash(password)
                )
            )
            connection.commit()
            flash("Admin account created successfully.", "success")
            return redirect(url_for("login"))
        except Exception:
            connection.rollback()
            flash("Admin email already exists.", "danger")
        finally:
            cursor.close()
            connection.close()

    return render_template("auth/admin_register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user or not check_password_hash(
            user["password_hash"],
            password
        ):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("user_dashboard"))

    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
def admin_dashboard():
    if not admin_required():
        flash("Admin login required.", "danger")
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role='candidate'")
    users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM jobs")
    jobs_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM resumes")
    screenings = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM resumes WHERE status='Selected'"
    )
    selected = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM resumes WHERE status='Rejected'"
    )
    rejected = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT AVG(ats_score) AS avg_ats, AVG(ai_score) AS avg_ai "
        "FROM resumes"
    )
    avg = cursor.fetchone()

    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id "
        "ORDER BY r.id DESC LIMIT 10"
    )
    recent = cursor.fetchall()

    cursor.close()
    connection.close()

    stats = {
        "users": users,
        "jobs": jobs_count,
        "screenings": screenings,
        "selected": selected,
        "rejected": rejected
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        avg=avg,
        recent=recent
    )


@app.route("/admin/candidates")
def admin_candidates():
    if not admin_required():
        return redirect(url_for("login"))

    status = request.args.get("status", "All")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if status == "All":
        cursor.execute(
            "SELECT r.*, j.title FROM resumes r "
            "JOIN jobs j ON r.job_id=j.id ORDER BY r.id DESC"
        )
    else:
        cursor.execute(
            "SELECT r.*, j.title FROM resumes r "
            "JOIN jobs j ON r.job_id=j.id "
            "WHERE r.status=%s ORDER BY r.id DESC",
            (status,)
        )

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "admin/candidates.html",
        rows=rows,
        status=status
    )


@app.route("/admin/candidate/<int:rid>")
def candidate_detail(rid):
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id WHERE r.id=%s",
        (rid,)
    )
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        flash("Candidate not found.", "danger")
        return redirect(url_for("admin_candidates"))

    return render_template("admin/candidate_detail.html", row=row)


@app.route("/admin/candidate/<int:rid>/decision/<decision>", methods=["POST"])
def candidate_decision(rid, decision):
    if not admin_required():
        return redirect(url_for("login"))

    if decision not in ["Selected", "Rejected"]:
        flash("Invalid decision.", "danger")
        return redirect(url_for("admin_candidates"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id, full_name FROM resumes WHERE id=%s",
        (rid,)
    )
    row = cursor.fetchone()

    if row:
        cursor.execute(
            "UPDATE resumes SET status=%s, decision_at=NOW() WHERE id=%s",
            (decision, rid)
        )

        cursor.execute(
            "INSERT INTO notifications(user_id,title,message) "
            "VALUES(%s,%s,%s)",
            (
                row["user_id"],
                "Recruitment Decision",
                "Your application status is " + decision + "."
            )
        )

        connection.commit()
        add_audit(
            "Candidate Decision",
            row["full_name"] + " marked as " + decision
        )

        flash("Candidate marked as " + decision + ".", "success")

    cursor.close()
    connection.close()

    return redirect(url_for("candidate_detail", rid=rid))


@app.route("/admin/jobs", methods=["GET", "POST"])
def admin_jobs():
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute(
            "INSERT INTO jobs "
            "(title,department,experience,location,description,required_skills) "
            "VALUES(%s,%s,%s,%s,%s,%s)",
            (
                request.form.get("title"),
                request.form.get("department"),
                request.form.get("experience"),
                request.form.get("location"),
                request.form.get("description"),
                request.form.get("required_skills")
            )
        )
        connection.commit()
        flash("Job created successfully.", "success")

    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("admin/jobs.html", rows=rows)


@app.route("/admin/jobs/toggle/<int:job_id>", methods=["POST"])
def toggle_job(job_id):
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE jobs SET status = "
        "CASE WHEN status='Open' THEN 'Closed' ELSE 'Open' END "
        "WHERE id=%s",
        (job_id,)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("admin_jobs"))


@app.route("/admin/screenings")
def admin_screenings():
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id ORDER BY r.id DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("admin/screenings.html", rows=rows)


@app.route("/admin/reports")
def admin_reports():
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) total, "
        "SUM(status='Selected') selected, "
        "SUM(status='Rejected') rejected, "
        "AVG(ats_score) avg_ats, AVG(ai_score) avg_ai "
        "FROM resumes"
    )
    totals = cursor.fetchone()

    cursor.execute(
        "SELECT j.title, COUNT(r.id) total, "
        "SUM(r.status='Selected') selected, "
        "SUM(r.status='Rejected') rejected, "
        "AVG(r.ats_score) avg_score "
        "FROM jobs j LEFT JOIN resumes r ON j.id=r.job_id "
        "GROUP BY j.id ORDER BY j.title"
    )
    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/reports.html",
        totals=totals,
        jobs=jobs
    )


@app.route("/admin/users")
def admin_users():
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("admin/users.html", rows=rows)


@app.route("/admin/audit")
def admin_audit():
    if not admin_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT a.*, u.full_name FROM audit_logs a "
        "LEFT JOIN users u ON a.admin_id=u.id "
        "ORDER BY a.id DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("admin/audit.html", rows=rows)


@app.route("/admin/settings")
def admin_settings():
    if not admin_required():
        return redirect(url_for("login"))

    return render_template("admin/settings.html")


@app.route("/jobs")
def user_jobs():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM jobs WHERE status='Open' ORDER BY id DESC"
    )
    jobs = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("user/jobs.html", jobs=jobs)


@app.route("/dashboard")
def user_dashboard():
    if not login_required() or session.get("role") == "admin":
        return redirect(url_for("login"))

    user = current_user()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) total FROM resumes WHERE user_id=%s",
        (user["id"],)
    )
    resumes = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) total FROM resumes WHERE user_id=%s",
        (user["id"],)
    )
    screenings = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) total FROM resumes "
        "WHERE user_id=%s AND status='Selected'",
        (user["id"],)
    )
    selected = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) total FROM resumes "
        "WHERE user_id=%s AND status='Rejected'",
        (user["id"],)
    )
    rejected = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id "
        "WHERE r.user_id=%s ORDER BY r.id DESC LIMIT 5",
        (user["id"],)
    )
    recent = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "user/dashboard.html",
        profile=user,
        stats={
            "resumes": resumes,
            "screenings": screenings,
            "selected": selected,
            "rejected": rejected
        },
        recent=recent
    )


@app.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if not login_required() or session.get("role") == "admin":
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        job_id = request.form.get("job_id")
        resume = request.files.get("resume")

        if not job_id or not resume or not resume.filename:
            flash("Please select a job and resume PDF.", "danger")
            cursor.close()
            connection.close()
            return redirect(url_for("upload_resume"))

        if not resume.filename.lower().endswith(".pdf"):
            flash("Only PDF files are allowed.", "danger")
            cursor.close()
            connection.close()
            return redirect(url_for("upload_resume"))

        user = current_user()
        job = get_job(job_id)

        filename = secure_filename(
            str(session["user_id"]) + "_" + resume.filename
        )
        path = os.path.join(UPLOAD_RESUMES, filename)
        resume.save(path)

        text = extract_text(path)
        detected = detect_skills(text)

        required = [
            item.strip().lower()
            for item in job["required_skills"].split(",")
            if item.strip()
        ]

        matching = [s for s in required if s in detected]
        missing = [s for s in required if s not in detected]

        ats = round(
            (len(matching) / len(required) * 100)
            if required else 0,
            2
        )

        ml_prediction, ml_confidence = predict_resume(text)

        ai_score = round(
            min(100, ats * 0.75 + ml_confidence * 0.25),
            2
        )

        ml_label = ml_prediction
        status = "Selected" if ai_score >= 70 else "Pending"

        cursor.execute(
            "INSERT INTO resumes "
            "(user_id,job_id,file_name,full_name,email,mobile,"
            "qualification,experience,location,detected_skills,"
            "matching_skills,missing_skills,ats_score,ai_score,"
            "ml_label,status,screened_at) "
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())",
            (
                user["id"],
                job_id,
                filename,
                user["full_name"],
                user["email"],
                user["mobile"],
                user["qualification"],
                user["experience"],
                user["location"],
                ", ".join(detected),
                ", ".join(matching),
                ", ".join(missing),
                ats,
                ai_score,
                ml_label,
                status
            )
        )

        connection.commit()

        resume_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO notifications(user_id,title,message) "
            "VALUES(%s,%s,%s)",
            (
                user["id"],
                "Resume Screening Complete",
                "Your resume was screened for " + job["title"] + "."
            )
        )
        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            url_for("screening_result", rid=resume_id)
        )

    cursor.execute(
        "SELECT * FROM jobs WHERE status='Open' ORDER BY title"
    )
    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("user/upload.html", jobs=jobs)


@app.route("/result/<int:rid>")
def screening_result(rid):
    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id "
        "WHERE r.id=%s AND r.user_id=%s",
        (rid, session["user_id"])
    )
    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        flash("Result not found.", "danger")
        return redirect(url_for("user_resumes"))

    return render_template(
        "user/result.html",
        row=row
    )


@app.route("/resumes")
def user_resumes():
    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id "
        "WHERE r.user_id=%s ORDER BY r.id DESC",
        (session["user_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("user/resumes.html", rows=rows)


@app.route("/screenings")
def user_screenings():
    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT r.*, j.title FROM resumes r "
        "JOIN jobs j ON r.job_id=j.id "
        "WHERE r.user_id=%s ORDER BY r.id DESC",
        (session["user_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("user/screenings.html", rows=rows)


@app.route("/reports")
def user_reports():
    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) total, AVG(ats_score) avg_ats, "
        "AVG(ai_score) avg_ai, "
        "SUM(status='Selected') selected, "
        "SUM(status='Rejected') rejected "
        "FROM resumes WHERE user_id=%s",
        (session["user_id"],)
    )
    summary = cursor.fetchone()

    cursor.execute(
        "SELECT j.title, AVG(r.ats_score) avg_ats "
        "FROM jobs j JOIN resumes r ON j.id=r.job_id "
        "WHERE r.user_id=%s GROUP BY j.id",
        (session["user_id"],)
    )
    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "user/reports.html",
        summary=summary,
        jobs=jobs
    )


@app.route("/notifications")
def user_notifications():
    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM notifications WHERE user_id=%s "
        "ORDER BY id DESC",
        (session["user_id"],)
    )
    rows = cursor.fetchall()

    cursor.execute(
        "UPDATE notifications SET is_read=1 WHERE user_id=%s",
        (session["user_id"],)
    )
    connection.commit()

    cursor.close()
    connection.close()

    return render_template(
        "user/notifications.html",
        rows=rows
    )


@app.route("/profile", methods=["GET", "POST"])
def user_profile():
    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        photo = request.files.get("photo")
        photo_name = None

        if photo and photo.filename:
            photo_name = secure_filename(
                str(session["user_id"]) + "_" + photo.filename
            )
            photo.save(os.path.join(UPLOAD_PHOTOS, photo_name))

        if photo_name:
            cursor.execute(
                "UPDATE users SET full_name=%s,mobile=%s,"
                "qualification=%s,experience=%s,location=%s,photo=%s "
                "WHERE id=%s",
                (
                    request.form.get("full_name"),
                    request.form.get("mobile"),
                    request.form.get("qualification"),
                    request.form.get("experience"),
                    request.form.get("location"),
                    photo_name,
                    session["user_id"]
                )
            )
        else:
            cursor.execute(
                "UPDATE users SET full_name=%s,mobile=%s,"
                "qualification=%s,experience=%s,location=%s "
                "WHERE id=%s",
                (
                    request.form.get("full_name"),
                    request.form.get("mobile"),
                    request.form.get("qualification"),
                    request.form.get("experience"),
                    request.form.get("location"),
                    session["user_id"]
                )
            )

        connection.commit()
        flash("Profile updated successfully.", "success")

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "user/profile.html",
        user=user
    )


@app.route("/resume-file/<name>")
def resume_file(name):
    return send_from_directory(
        UPLOAD_RESUMES,
        name,
        as_attachment=True
    )


@app.route("/photo-file/<name>")
def photo_file(name):
    return send_from_directory(
        UPLOAD_PHOTOS,
        name
    )


@app.route("/admin/export")
def export_report():
    if not admin_required():
        return redirect(url_for("login"))

    import csv
    from io import StringIO
    from flask import Response

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT r.id,r.full_name,r.email,j.title,"
        "r.ats_score,r.ai_score,r.status,r.screened_at "
        "FROM resumes r JOIN jobs j ON r.job_id=j.id "
        "ORDER BY r.id DESC"
    )
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Candidate", "Email", "Job",
        "ATS", "AI", "Status", "Screened"
    ])

    for row in rows:
        writer.writerow([
            row["id"],
            row["full_name"],
            row["email"],
            row["title"],
            row["ats_score"],
            row["ai_score"],
            row["status"],
            row["screened_at"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=screening_report.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
