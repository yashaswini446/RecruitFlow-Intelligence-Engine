"""Database + app configuration. Override via environment variables."""
import os

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3306")),
    "user":     os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "naksh@143"),
    "database": os.getenv("MYSQL_DB", "recruit"),
}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXT = {"pdf", "docx", "txt"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
