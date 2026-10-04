"""
RecruitFlow Intelligence Engine — Flask app.

Run:
    pip install -r requirements.txt
    mysql < sql/schema.sql
    python app.py
Open http://localhost:5000
"""
import os
import re
import config
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename

from config import UPLOAD_DIR, ALLOWED_EXT, MAX_CONTENT_LENGTH
from db import query
from optimizer import (
    read_resume, extract_skills, extract_experience,
    resume_hash, optimize_score,
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "change-me"
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def get_db_setting(name, default):
    value = getattr(config, name, None)
    return value or os.getenv(name, default)


def get_db_settings():
    return {
        "host": getattr(config, "DB_HOST", None) or os.getenv("DB_HOST", "localhost"),
        "user": getattr(config, "DB_USER", None) or os.getenv("DB_USER", "root"),
        "password": getattr(config, "DB_PASSWORD", None) or os.getenv("DB_PASSWORD", "naksh@143"),
        "database": getattr(config, "DB_NAME", None) or os.getenv("DB_NAME", "recruitflow"),
        "port": int(getattr(config, "DB_PORT", None) or os.getenv("DB_PORT", 3306)),
    }


def get_db_connection():
    settings = get_db_settings()
    try:
        import mysql.connector as mysql_client

        return mysql_client.connect(
            host=settings["host"],
            user=settings["user"],
            password=settings["password"],
            database=settings["database"],
            port=settings["port"],
            autocommit=True,
        )
    except ImportError:
        import pymysql

        return pymysql.connect(
            host=settings["host"],
            user=settings["user"],
            password=settings["password"],
            db=settings["database"],
            port=settings["port"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )


def query(sql, params=None, fetch=False, many=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) if hasattr(conn, "cursor") else conn.cursor()
    try:
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall() if many else cursor.fetchone()
        conn.commit()
        return None
    finally:
        cursor.close()
        conn.close()


def allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ---------- Routes ----------
@app.route("/")
def index():
    jobs       = query("SELECT * FROM jobs ORDER BY id DESC", fetch=True, many=True)
    candidates = query("SELECT * FROM candidates ORDER BY id DESC", fetch=True, many=True)
    return render_template("index.html", jobs=jobs, candidates=candidates)


@app.route("/jobs", methods=["POST"])
def create_job():
    title  = request.form["title"].strip()
    skills = request.form["required_skills"].strip()
    exp    = int(request.form.get("min_experience") or 0)
    desc   = request.form.get("description", "").strip()
    if not title or not skills:
        flash("Job title and required skills are required.", "error")
        return redirect(url_for("index"))
    query(
        "INSERT INTO jobs (title, required_skills, min_experience, description) VALUES (%s,%s,%s,%s)",
        (title, skills, exp, desc),
    )
    flash(f"Job “{title}” created.", "success")
    return redirect(url_for("index"))


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    query("DELETE FROM jobs WHERE id=%s", (job_id,))
    return redirect(url_for("index"))


@app.route("/candidates", methods=["POST"])
def upload_resumes():
    files = request.files.getlist("resumes")
    added, dupes, bad = 0, 0, 0
    for f in files:
        if not f or not f.filename:
            continue
        if not allowed(f.filename):
            bad += 1
            continue
        fname = secure_filename(f.filename)
        path  = os.path.join(UPLOAD_DIR, fname)
        f.save(path)
        try:
            text = read_resume(path)
        except Exception:
            bad += 1
            continue
        h = resume_hash(text)
        existing = query("SELECT id FROM candidates WHERE resume_hash=%s", (h,), fetch=True)
        if existing:
            dupes += 1
            continue
        # naive name + email extraction
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        name = os.path.splitext(fname)[0].replace("_", " ").title()
        skills = ", ".join(extract_skills(text))
        years  = extract_experience(text)
        query(
            """INSERT INTO candidates
               (name, email, experience_years, skills, raw_text, resume_hash)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (name, email_match.group(0) if email_match else None,
             years, skills, text[:60000], h),
        )
        added += 1
    flash(f"Uploaded: {added} added, {dupes} duplicate, {bad} invalid.", "success")
    return redirect(url_for("index"))


@app.route("/candidates/<int:cid>/delete", methods=["POST"])
def delete_candidate(cid):
    query("DELETE FROM candidates WHERE id=%s", (cid,))
    return redirect(url_for("index"))


@app.route("/optimize/<int:job_id>", methods=["POST"])
def optimize(job_id):
    """The Optimization Button endpoint."""
    job = query("SELECT * FROM jobs WHERE id=%s", (job_id,), fetch=True)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    candidates = query("SELECT * FROM candidates", fetch=True, many=True) or []

    # 1. Wipe previous results for this job
    query("DELETE FROM match_results WHERE job_id=%s", (job_id,))

    # 2. Score everyone
    scored = []
    for c in candidates:
        result = optimize_score(c, job)
        result["candidate"] = c
        scored.append(result)

    # 3. Rank by optimized score
    scored.sort(key=lambda r: r["optimized_score"], reverse=True)

    # 4. Persist
    for rank, r in enumerate(scored, start=1):
        query(
            """INSERT INTO match_results
               (candidate_id, job_id, base_score, optimized_score,
                matched_skills, skill_gaps, rank_position)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (r["candidate"]["id"], job_id, r["base_score"], r["optimized_score"],
             r["matched_skills"], r["skill_gaps"], rank),
        )

    return redirect(url_for("results", job_id=job_id))


@app.route("/results/<int:job_id>")
def results(job_id):
    job = query("SELECT * FROM jobs WHERE id=%s", (job_id,), fetch=True)
    rows = query(
        """SELECT m.*, c.name, c.email, c.experience_years, c.skills
           FROM match_results m JOIN candidates c ON c.id = m.candidate_id
           WHERE m.job_id=%s ORDER BY m.rank_position ASC""",
        (job_id,), fetch=True, many=True,
    )
    return render_template("results.html", job=job, rows=rows or [])


@app.route("/api/results/<int:job_id>")
def api_results(job_id):
    rows = query(
        """SELECT m.rank_position, c.name, m.base_score, m.optimized_score,
                  m.matched_skills, m.skill_gaps
           FROM match_results m JOIN candidates c ON c.id = m.candidate_id
           WHERE m.job_id=%s ORDER BY m.rank_position""",
        (job_id,), fetch=True, many=True,
    )
    return jsonify(rows or [])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
