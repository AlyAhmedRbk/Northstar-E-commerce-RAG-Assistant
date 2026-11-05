from flask import Blueprint, current_app, jsonify, request

from app.config import Config
from app.services.llm_service import LLMServiceError
from app.services.rag_service import answer_question


chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/")
def chat():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "A valid JSON request body is required."
        }), 400

    question = payload.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Please enter a question."
        }), 400

    question = question.strip()

    if len(question) > Config.MAX_QUESTION_LENGTH:
        return jsonify({
            "error": (
                f"Your question cannot exceed "
                f"{Config.MAX_QUESTION_LENGTH} characters."
            )
        }), 400

    try:
        result = answer_question(question)

        return jsonify({
            "status": "success",
            **result,
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except LLMServiceError:
        current_app.logger.exception("LLM provider request failed")

        return jsonify({
            "error": "The AI assistant is temporarily unavailable. Please try again."
        }), 502

    except Exception:
        current_app.logger.exception("Chat request failed")

        return jsonify({
            "error": "Something went wrong while processing your question."
        }), 500
