import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Configuration locale de la démo Operation EVO."""

    SECRET_KEY = os.getenv("SECRET_KEY", "operation-evo-demo-change-me")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", BASE_DIR / "data" / "app.db"))
    SQLITE_DB_PATH_STR = str(SQLITE_DB_PATH)

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SYSTEM_EMAIL_RECIPIENT = os.getenv(
        "SYSTEM_EMAIL_RECIPIENT", "support@operation-evo.local"
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8

    DEMO_ADMIN_EMAIL = os.getenv("DEMO_ADMIN_EMAIL", "admin@operation-evo.local")
    DEMO_ADMIN_PASSWORD = os.getenv("DEMO_ADMIN_PASSWORD", "Admin123!")
    DEMO_AGENT_EMAIL = os.getenv("DEMO_AGENT_EMAIL", "agent@operation-evo.local")
    DEMO_AGENT_PASSWORD = os.getenv("DEMO_AGENT_PASSWORD", "Agent123!")
