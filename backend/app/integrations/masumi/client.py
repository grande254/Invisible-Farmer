import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


load_dotenv()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MasumiLocalClient:
    def __init__(self):
        self.mode = os.getenv("MASUMI_MODE", "local")
        self.registry_url = os.getenv("MASUMI_REGISTRY_SERVICE_URL", "http://localhost:3000").rstrip("/")
        self.payment_url = os.getenv("MASUMI_PAYMENT_SERVICE_URL", "http://localhost:3001").rstrip("/")
        self.agent_identifier = os.getenv(
            "MASUMI_AGENT_IDENTIFIER",
            "local-invisible-farmer-credit-review-agent",
        )
        self.agent_name = os.getenv("MASUMI_AGENT_NAME", "Invisible Farmer Credit Review Agent")
        self.agent_version = os.getenv("MASUMI_AGENT_VERSION", "v2")
        self.payment_type = os.getenv("MASUMI_PAYMENT_TYPE", "mocked")

    def _probe_url(self, base_url: str) -> dict:
        probe_targets = [
            base_url,
            f"{base_url}/health",
            f"{base_url}/api/health",
        ]

        last_error = None

        for url in probe_targets:
            try:
                response = requests.get(url, timeout=3)

                return {
                    "reachable": True,
                    "url": url,
                    "status_code": response.status_code,
                }
            except Exception as exc:
                last_error = str(exc)

        return {
            "reachable": False,
            "url": base_url,
            "error": last_error,
        }

    def service_status(self) -> dict:
        registry = self._probe_url(self.registry_url)
        payment = self._probe_url(self.payment_url)

        return {
            "mode": self.mode,
            "agent_identifier": self.agent_identifier,
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "payment_type": self.payment_type,
            "registry_service": registry,
            "payment_service": payment,
            "local_masumi_available": registry["reachable"] and payment["reachable"],
            "checked_at": now_iso(),
        }


masumi_client = MasumiLocalClient()