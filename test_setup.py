import os
import sys

# Ensure app path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.database.database import init_db, db_session, engine
    from app.models.models import Candidate, Job, Education, Experience, Skill, AIAnalysis, MatchResult, Base
    print("Imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("Testing DB initialization and table generation...")
    try:
        init_db()
        print("Dropping existing tables to re-apply new schema...")
        Base.metadata.drop_all(bind=engine)
        init_db()
        print("Success! Database initialized and tables verified.")
    except Exception as e:
        print(f"Error during DB initialization: {e}")
        sys.exit(1)
