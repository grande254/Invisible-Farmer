def con(text: str) -> dict:
    return {
        "type": "CON",
        "text": text,
    }


def end(text: str) -> dict:
    return {
        "type": "END",
        "text": text,
    }


def normalize_text(value: str | None) -> str:
    return (value or "").strip()


def parse_ussd_path(text: str | None) -> list[str]:
    text = normalize_text(text)

    if not text:
        return []

    return [part.strip() for part in text.split("*") if part.strip()]


def compact(text: str, limit: int = 180) -> str:
    text = normalize_text(text)

    if len(text) <= limit:
        return text

    return text[: limit - 3].rstrip() + "..."