"""Application factory for Fly Happy International Travels."""
import os
from datetime import datetime

from flask import Flask, render_template

from config import config_map
from app.extensions import db, login_manager, csrf


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.booking import booking_bp
    from app.routes.payment import payment_bp
    from app.routes.customer import customer_bp
    from app.routes.admin import admin_bp
    from app.routes.chatbot import chatbot_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)

    # Exempt chatbot JSON API from CSRF (uses its own lightweight checks)
    csrf.exempt(chatbot_bp)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Context processor: company info available in every template
    @app.context_processor
    def inject_company_info():
        return {
            "company_name": app.config["COMPANY_NAME"],
            "company_short_name": app.config["COMPANY_SHORT_NAME"],
            "company_license": app.config["COMPANY_LICENSE"],
            "company_tagline": app.config["COMPANY_TAGLINE"],
            "company_phone": app.config["COMPANY_PHONE"],
            "company_emergency_phone": app.config["COMPANY_EMERGENCY_PHONE"],
            "company_whatsapp": app.config["COMPANY_WHATSAPP"],
            "company_email": app.config["COMPANY_EMAIL"],
            "company_address": app.config["COMPANY_ADDRESS"],
            "company_hours": app.config["COMPANY_HOURS"],
            "current_year": datetime.utcnow().year,
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    # CLI command to (re)initialize + seed the database
    @app.cli.command("init-db")
    def init_db():
        """Drop, create and seed the database with sample data."""
        from app.seed import run_seed
        with app.app_context():
            db.drop_all()
            db.create_all()
            run_seed()
        print("Database initialized and seeded successfully.")

    return app
