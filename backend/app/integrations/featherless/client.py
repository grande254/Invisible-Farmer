import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.integrations.featherless.prompts import FEATHERLESS_SYSTEM_PROMPT


load_dotenv()


def parse_json_response(text: str) -> dict:
    cleaned = (text or "").strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return json.loads(cleaned)


def get_fallback_models() -> list[str]:
    primary = os.getenv("FEATHERLESS_MODEL", "").strip()

    raw = os.getenv("FEATHERLESS_FALLBACK_MODELS", "").strip()

    models = []

    if primary:
        models.append(primary)

    if raw:
        models.extend([item.strip() for item in raw.split(",") if item.strip()])

    deduped = []

    for model in models:
        if model not in deduped:
            deduped.append(model)

    return deduped


class FeatherlessClient:
    def __init__(self):
        self.api_key = os.getenv("FEATHERLESS_API_KEY")
        self.base_url = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
        self.models = get_fallback_models()

        if not self.api_key:
            raise RuntimeError("FEATHERLESS_API_KEY is missing.")

        if not self.models:
            raise RuntimeError("FEATHERLESS_MODEL is missing.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def generate_business_explanation(self, payload: dict[str, Any]) -> dict:
        last_error = None

        for model in self.models:
            for attempt in range(1, 4):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": FEATHERLESS_SYSTEM_PROMPT,
                            },
                            {
                                "role": "user",
                                "content": json.dumps(payload, ensure_ascii=False),
                            },
                        ],
                        temperature=0.2,
                        max_tokens=1800,
                    )

                    content = response.choices[0].message.content or ""
                    parsed = parse_json_response(content)

                    parsed["_featherless_model_used"] = model
                    parsed["_featherless_attempt"] = attempt

                    return parsed

                except Exception as exc:
                    last_error = exc
                    error_text = str(exc)

                    is_retryable = any(
                        code in error_text
                        for code in [
                            "503",
                            "502",
                            "504",
                            "429",
                            "Service Unavailable",
                            "temporarily unavailable",
                            "rate limit",
                        ]
                    )

                    if not is_retryable:
                        break

                    time.sleep(attempt * 2)

        raise RuntimeError(f"Featherless request failed after retries. Last error: {last_error}")


featherless_client = FeatherlessClient()