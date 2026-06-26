import json
from pathlib import Path

from app.schemas.farmer import Farmer


APP_DIR = Path(__file__).resolve().parents[2]
FARMERS_PATH = APP_DIR / "data" / "farmers.seed.json"


def read_json_file(path: Path):
    """
    Reads JSON safely even if the file was created by PowerShell
    with a UTF-8 BOM.
    """
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def load_farmers() -> list[dict]:
    raw = read_json_file(FARMERS_PATH)
    farmers = [Farmer(**item).model_dump() for item in raw]
    return farmers


def list_farmers() -> list[dict]:
    return load_farmers()


def get_farmer_by_id(farmer_id: str) -> dict | None:
    normalized_id = farmer_id.strip().upper()

    for farmer in load_farmers():
        if farmer["farmer_id"].upper() == normalized_id:
            return farmer

    return None