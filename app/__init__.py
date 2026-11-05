import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template

from app.config import BASE_DIR, Config
from app.routes.chat import chat_bp
from app.routes.health import health_bp


def configure_logging(app):
    log_directory = BASE_DIR / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file = log_directory / "application.log"

    # Avoid adding duplicate handlers when creating multiple app instances.
    if not any(
        isinstance(handler, RotatingFileHandler)
        and getattr(handler, "baseFilename", None) == str(log_file)
        for handler in app.logger.handlers
    ):
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))

        app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    Config.validate()

    Config.CHROMA_PERSIST_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    configure_logging(app)

    # Customer-facing routes only.
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        if app.config["APP_ENV"] == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Resource not found."
        }), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "error": "Request exceeds the maximum allowed size."
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Unexpected application error")

        return jsonify({
            "error": "An internal server error occurred."
        }), 500

    app.logger.info("E-commerce RAG Assistant initialized")

    return app
