import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

from app.database.database import init_db, db_session
from app.models.models import Job, Candidate, MatchResult, WorkflowRule
from sqlalchemy import func
from app.routes.candidate_routes import candidate_bp
from app.routes.job_routes import job_bp
from app.routes.ats_routes import ats_bp
from app.routes.workflow_routes import workflow_bp
from config import MAX_CONTENT_LENGTH

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "recruitflow-secret-key-12345")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Register Blueprints
app.register_blueprint(candidate_bp)
app.register_blueprint(job_bp)
app.register_blueprint(ats_bp)
app.register_blueprint(workflow_bp)

@app.route("/")
def index():
    jobs = db_session.query(Job).order_by(Job.id.desc()).all()
    candidates = db_session.query(Candidate).order_by(Candidate.candidate_id.desc()).all()
    
    # Format candidates list for basic display in the main page table
    candidate_list = []
    for c in candidates:
        skills_str = ", ".join([s.skill_name for s in c.skills])
        candidate_list.append({
            "id": c.candidate_id,
            "name": c.full_name,
            "email": c.email,
            "experience_years": c.years_of_experience,
            "skills": skills_str,
            "is_duplicate": c.is_duplicate
        })

        
    # Stats calculations
    total_candidates = len(candidates)
    total_jobs = len(jobs)
    
    avg_score_query = db_session.query(func.avg(MatchResult.optimized_score)).scalar()
    avg_score = round(float(avg_score_query), 1) if avg_score_query is not None else 0.0
    
    active_rules_count = db_session.query(WorkflowRule).filter_by(is_active=1).count()
    
    stats = {
        "candidates": total_candidates,
        "jobs": total_jobs,
        "avg_score": avg_score,
        "active_rules": active_rules_count
    }
        
    return render_template("index.html", jobs=jobs, candidates=candidate_list, stats=stats)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    # Ensure database tables exist
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")
    
    # Start Flask server
    port = int(os.getenv("PORT", 5002))
    app.run(debug=True, use_reloader=True, port=port)
