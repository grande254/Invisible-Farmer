import json
from pathlib import Path
from threading import Lock


APP_DIR = Path(__file__).resolve().parents[2]
STORE_PATH = APP_DIR / "data" / "local" / "masumi_jobs.json"

STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

_LOCK = Lock()


def _read_store() -> dict:
    if not STORE_PATH.exists():
        return {"jobs": {}}

    text = STORE_PATH.read_text(encoding="utf-8-sig").strip()

    if not text:
        return {"jobs": {}}

    return json.loads(text)


def _write_store(data: dict) -> None:
    STORE_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_job(job: dict) -> dict:
    with _LOCK:
        data = _read_store()
        data.setdefault("jobs", {})
        data["jobs"][job["job_id"]] = job
        _write_store(data)

    return job


def get_job(job_id: str) -> dict | None:
    data = _read_store()
    return data.get("jobs", {}).get(job_id)


def list_jobs() -> list[dict]:
    data = _read_store()
    return list(data.get("jobs", {}).values())


def update_job(job_id: str, updates: dict) -> dict:
    with _LOCK:
        data = _read_store()
        jobs = data.setdefault("jobs", {})

        if job_id not in jobs:
            raise ValueError(f"Masumi job {job_id} not found")

        jobs[job_id].update(updates)
        _write_store(data)

        return jobs[job_id]