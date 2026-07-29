"""Application configuration for Fly Happy International Travels."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Core
    SECRET_KEY = os.environ.get("SECRET_KEY", "fly-happy-dev-secret-key-PR-5199-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "flyhappy.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 hours

    # Company info (used across templates)
    COMPANY_NAME = "Fly Happy International Travels"
    COMPANY_SHORT_NAME = "Fly Happy"
    COMPANY_LICENSE = "PR-5199"
    COMPANY_TAGLINE = "Your Journey, Our Passion"
    COMPANY_PHONE = "+92 300 1234567"
    COMPANY_EMERGENCY_PHONE = "+92 300 9998888"
    COMPANY_WHATSAPP = "+92 300 1234567"
    COMPANY_EMAIL = "info@flyhappytravels.com"
    COMPANY_ADDRESS = "Suite 401, Business Tower, Blue Area, Islamabad, Pakistan"
    COMPANY_HOURS = "Mon - Sat: 9:00 AM - 8:00 PM"

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
