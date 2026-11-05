import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"true", "1", "yes", "on"}


class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DEBUG = get_bool("DEBUG", False)

    SECRET_KEY = os.getenv("SECRET_KEY", "")

    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )

    KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

    # Retained for compatibility with the old internal upload workflow.
    UPLOAD_FOLDER = Path(
        os.getenv(
            "UPLOAD_FOLDER",
            str(BASE_DIR / "data" / "uploads"),
        )
    )

    CHROMA_PERSIST_DIRECTORY = Path(
        os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            str(BASE_DIR / "data" / "chroma"),
        )
    )

    CHROMA_COLLECTION_NAME = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "ecommerce_knowledge",
    )

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 450))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 75))
    TOP_K = int(os.getenv("TOP_K", 5))

    SIMILARITY_THRESHOLD = float(
        os.getenv("SIMILARITY_THRESHOLD", "0.30")
    )

    FASTROUTER_API_KEY = os.getenv("FASTROUTER_API_KEY", "")
    FASTROUTER_BASE_URL = os.getenv("FASTROUTER_BASE_URL", "")
    FASTROUTER_MODEL = os.getenv("FASTROUTER_MODEL", "")

    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "45"))
    LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))

    MAX_QUESTION_LENGTH = int(
        os.getenv("MAX_QUESTION_LENGTH", "1000")
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = APP_ENV == "production"

    MAX_CHUNK_SIZE = 600

    @classmethod
    def validate(cls):
        if cls.APP_ENV == "production":
            if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
                raise RuntimeError(
                    "Production requires a SECRET_KEY of at least 32 characters."
                )

            if cls.DEBUG:
                raise RuntimeError(
                    "DEBUG must be disabled in production."
                )

        if cls.CHUNK_SIZE <= 0:
            raise RuntimeError("CHUNK_SIZE must be greater than zero.")

        if not 0 <= cls.CHUNK_OVERLAP < cls.CHUNK_SIZE:
            raise RuntimeError(
                "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
            )

        if cls.TOP_K < 1:
            raise RuntimeError("TOP_K must be at least 1.")

        if not 0 <= cls.SIMILARITY_THRESHOLD <= 1:
            raise RuntimeError(
                "SIMILARITY_THRESHOLD must be between 0 and 1."
            )

        if cls.MAX_CONTENT_LENGTH < 1:
            raise RuntimeError("MAX_CONTENT_LENGTH must be positive.")

        if cls.MAX_QUESTION_LENGTH < 1:
            raise RuntimeError("MAX_QUESTION_LENGTH must be positive.")

        if cls.LLM_TIMEOUT <= 0:
            raise RuntimeError("LLM_TIMEOUT must be positive.")

        if cls.LLM_MAX_RETRIES < 0:
            raise RuntimeError("LLM_MAX_RETRIES cannot be negative.")
