from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "E-commerce RAG Assistant",
    }), 200


@health_bp.get("/ready")
def readiness():
    return jsonify({
        "status": "ready",
        "checks": {
            "application": "ok",
        },
    }), 200