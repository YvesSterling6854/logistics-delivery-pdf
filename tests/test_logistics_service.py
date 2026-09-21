import pytest
from src.logistics_service import Shipment, create_delivery_document


class StubClient:
    def generate(self, markdown: str):
        assert "Status: EXCEPTION" in markdown
        assert "Dock closed" in markdown
        return {"document_id": "doc-test"}


def test_exception_requires_a_reason_and_renders_document():
    shipment = Shipment("TRK-9", "A", "B", None, (), "Dock closed")
    assert create_delivery_document(shipment, StubClient()) == {"document_id": "doc-test"}


def test_pending_without_reason_is_rejected():
    with pytest.raises(ValueError):
        create_delivery_document(Shipment("TRK-9", "A", "B", None, ()), StubClient())
