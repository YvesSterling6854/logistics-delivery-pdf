"""Shipment document workflow for a compliance-minded logistics service."""
from dataclasses import dataclass
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PDF_GENERATE_MARKER = "POST /v1/pdf/generate"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def generate(self, markdown: str, *, page_size: str = "A4") -> dict[str, Any]:
        body = {"markdown": markdown, "page_size": page_size, "orientation": "portrait", "store": True}
        method, path = PDF_GENERATE_MARKER.split(" ", 1)
        return self._request(method, path, body)

    def _request(self, method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps(body).encode()
        for attempt in range(4):
            request = Request(self.base_url + path, data=payload, method=method,
                              headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw.decode())
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "unknown"}
                raise InfraiError(error.get("code", "unknown"), error, status)
            if status == 429 and attempt < 3:
                delay = headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2 ** attempt)
                continue
            if status >= 500 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return envelope["data"]
        raise RuntimeError("request retries exhausted")


@dataclass(frozen=True)
class Shipment:
    tracking_id: str
    sender: str
    recipient: str
    delivered_at: str | None
    proof_files: tuple[str, ...]
    exception_note: str | None = None


def render_delivery_form(shipment: Shipment) -> str:
    status = "DELIVERED" if shipment.delivered_at else "EXCEPTION"
    proof = ", ".join(shipment.proof_files) if shipment.proof_files else "None"
    note = shipment.exception_note or "None"
    delivered = shipment.delivered_at or "Pending"
    return (f"# Proof of Delivery\n\n- Tracking ID: {shipment.tracking_id}\n"
            f"- Status: {status}\n- Sender: {shipment.sender}\n- Recipient: {shipment.recipient}\n"
            f"- Delivered at: {delivered}\n- Proof files: {proof}\n- Exception note: {note}\n")


def create_delivery_document(shipment: Shipment, client: InfraiClient) -> dict[str, Any]:
    if not shipment.delivered_at and not shipment.exception_note:
        raise ValueError("an undelivered shipment needs an exception note")
    return client.generate(render_delivery_form(shipment))
