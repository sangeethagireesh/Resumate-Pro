import os
import json
import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
import PyPDF2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set a fixed secret key for session management
app.secret_key = os.getenv("SECRET_KEY", "this_is_a_secret_key_for_testing")

DATABASE = 'users.db'

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load job keywords JSON once
try:
    with open("job_keywords.json", "r") as f:
        keyword_dataset = json.load(f)
    logging.info("Loaded job_keywords.json successfully")
except Exception as e:
    logging.error(f"Error loading job_keywords.json: {e}")
    keyword_dataset = {}

# ------------------ Database helpers ------------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ------------------ Utility functions ------------------

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.lower()
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        return ""

def get_job_keywords(job_title):
    value = keyword_dataset.get(job_title.lower(), [])
    # value could be list or dict, if dict return its 'keywords' list
    if isinstance(value, dict):
        return value.get("keywords", [])
    return value

def get_resume_skills(resume_text):
    words = set(resume_text.lower().split())
    all_keywords = []
    for v in keyword_dataset.values():
        if isinstance(v, dict):
            all_keywords.extend(v.get("keywords", []))
        elif isinstance(v, list):
            all_keywords.extend(v)
    skills = [kw for kw in all_keywords if kw.lower() in words]
    return list(set(skills))

def suggest_improvements(job_title, resume_text):
    keywords = get_job_keywords(job_title)
    resume_words = resume_text.lower().split()
    missing_keywords = [kw for kw in keywords if kw.lower() not in resume_words]
    if not missing_keywords:
        return {
            "heading": "Suggestions",
            "points": ["Your resume covers most of the important skills. Good job!"]
        }
    points = [f"Consider adding the keyword: '{kw}'" for kw in missing_keywords[:5]]
    return {
        "heading": "Suggestions",
        "points": points
    }

def calculate_ats_score(keywords, skills):
    matched = [kw for kw in keywords if kw in skills]
    missing = [kw for kw in keywords if kw not in skills]
    score = int(len(matched) / len(keywords) * 100) if keywords else 0
    return score, matched, missing

# ------------------ Routes ------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password are required.", "warning")
            return render_template("register.html")

        db = get_db()
        existing = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("User already exists. Please choose a different username.", "warning")
            return render_template("register.html")
        hashed_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        db.commit()
        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    jobs = list(keyword_dataset.keys())
    return render_template("dashboard.html", username=session.get("user"), jobs=jobs)

@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        job_title = request.form.get("job_title", "").strip()
        resume_file = request.files.get("resume")

        if not job_title or not resume_file:
            return jsonify({"error": "Missing job title or resume file"}), 400

        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            return jsonify({"error": "Failed to extract text from resume PDF."}), 400

        job_keywords = get_job_keywords(job_title)
        resume_skills = get_resume_skills(resume_text)
        score, matched, missing = calculate_ats_score(job_keywords, resume_skills)
        suggestions = suggest_improvements(job_title, resume_text)

        return jsonify({
            "score": score,
            "matched": matched,
            "missing": missing,
            "suggestions": suggestions.get("points", [])
        })
    except Exception as e:
        logging.error(f"Error in analyze_resume: {e}", exc_info=True)
        return jsonify({"error": "Internal server error."}), 500

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
