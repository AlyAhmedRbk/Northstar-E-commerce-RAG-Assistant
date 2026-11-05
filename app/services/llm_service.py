from functools import lru_cache

from openai import OpenAI, APIError

from app.config import Config


class LLMServiceError(Exception):
    """Raised when the LLM provider cannot generate a response."""


@lru_cache(maxsize=1)
def get_llm_client():
    if not Config.FASTROUTER_API_KEY:
        raise LLMServiceError("LLM API key is not configured.")

    if not Config.FASTROUTER_BASE_URL:
        raise LLMServiceError("LLM base URL is not configured.")

    if not Config.FASTROUTER_MODEL:
        raise LLMServiceError("LLM model is not configured.")

    return OpenAI(
        api_key=Config.FASTROUTER_API_KEY,
        base_url=Config.FASTROUTER_BASE_URL,
        timeout=Config.LLM_TIMEOUT,
        max_retries=Config.LLM_MAX_RETRIES,
    )


def generate_completion(
    system_prompt: str,
    user_prompt: str,
) -> str:
    try:
        client = get_llm_client()

        response = client.chat.completions.create(
            model=Config.FASTROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.2,
            max_tokens=600,
        )

        if not response.choices:
            raise LLMServiceError(
                "The LLM provider returned an empty response."
            )

        answer = response.choices[0].message.content

        if not answer or not answer.strip():
            raise LLMServiceError(
                "The LLM provider returned an empty answer."
            )

        return answer.strip()

    except LLMServiceError:
        raise

    except APIError as error:
        raise LLMServiceError(
            "The LLM provider request failed."
        ) from error

    except Exception as error:
        raise LLMServiceError(
            "An unexpected LLM service error occurred."
        ) from error
