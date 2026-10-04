# RecruitFlow Intelligence Engine

AI-powered resume ↔ job matching with a one-click **Optimization Button**.
Stack: **Python (Flask) + MySQL + HTML/CSS**.

## Features
- Upload resumes (PDF / DOCX / TXT) — auto-extracts skills + experience.
- Define jobs with required skills + minimum experience.
- **⚡ Optimize button** runs the AI pipeline:
  1. Deduplicates resumes (SHA-256 of normalized text).
  2. Normalizes skill names using a synonym dictionary (`js → javascript`, etc.).
  3. Computes a base score (skill overlap %).
  4. Recalculates an **optimized score** with experience, density and gap-penalty heuristics.
  5. Ranks candidates per job and stores results in MySQL.
- Results page shows ranking, compatibility %, matched skills and **skill-gap analysis**.
- JSON API: `GET /api/results/<job_id>`.

## Setup

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Create the database
mysql -u root -p < sql/schema.sql

# 3. Configure DB (env vars override defaults in config.py)
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpass
export MYSQL_DB=recruitflow

# 4. Run
python app.py
# open http://localhost:5000
```

## Project layout
```
recruitflow/
├── app.py              # Flask routes
├── optimizer.py        # AI scoring + parsing engine
├── db.py               # MySQL helper
├── config.py
├── requirements.txt
├── sql/schema.sql
├── templates/          # Jinja2 HTML
├── static/style.css
└── uploads/            # Saved resumes
```

## How the Optimization Button works
`POST /optimize/<job_id>` →
1. Loads all candidates + the job.
2. For each candidate calls `optimizer.optimize_score()`:
   - `base = overlap(required, candidate) / |required|`
   - `+ experience bonus (up to +10)`
   - `+ skill-density bonus (up to +8)`
   - `– gap penalty (up to –15)`
   - `+5` calibration, clamped to `[0, 100]`.
3. Sorts descending, writes `match_results` rows with `rank_position`.
4. Redirects to `/results/<job_id>`.

Extend `SKILL_SYNONYMS` / `SKILL_VOCAB` in `optimizer.py` to improve matching accuracy for your domain.
