import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

# Ensure backend/ is on sys.path so `app.*` imports work when running from repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.calculator import compute_emissions
from app.document_ai import extract_fields
from app.main import app
from app.predictor import forecast_next_month
from app import rag as rag_module
from app import llm as llm_module


def test_extract_fields_energy_regex():
    messy_text = """
    Invoice #123
    Electric Cons.: 1,250.5 kWh
    Some other text...
    """
    fields = extract_fields(messy_text)
    assert fields["energy_kwh"] == 1250.5


def test_compute_emissions_electricity():
    emissions = compute_emissions({"energy_kwh": 100})
    assert emissions["total_kgco2"] == pytest.approx(23.3, rel=1e-3)


def test_predictor_forecast_next_month():
    model_path = ROOT / "data" / "predictor_model.pkl"
    assert model_path.exists(), "predictor_model.pkl is missing"

    history = [
        {"fields": {"date": "2024-01-01"}, "emissions": {"total_kgco2": 10}},
        {"fields": {"date": "2024-02-01"}, "emissions": {"total_kgco2": 12}},
        {"fields": {"date": "2024-03-01"}, "emissions": {"total_kgco2": 11}},
        {"fields": {"date": "2024-04-01"}, "emissions": {"total_kgco2": 13}},
    ]
    forecast = forecast_next_month(history)
    assert forecast["predicted_kgco2"] is not None
    assert isinstance(forecast["predicted_kgco2"], float)


def test_rag_store_document_mock(monkeypatch):
    # Ensure env vars exist so rag import does not raise.
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_API_KEY", "dummy")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.created = False

        class _CollectionList:
            def __init__(self, collections):
                self.collections = collections

        def get_collections(self):
            return self._CollectionList(collections=[])

        def create_collection(self, collection_name, vectors_config):
            self.created = True

        def upsert(self, collection_name, points):
            return True

        def scroll(self, collection_name, limit, with_payload):
            return [], None

    # Swap out the client to avoid any real network calls.
    monkeypatch.setattr(rag_module, "client", DummyClient())

    doc_id = rag_module.store_document({"energy_kwh": 1.0}, {"total_kgco2": 0.233})
    assert isinstance(doc_id, str)


def test_llm_generate_explanation_mock(monkeypatch):
    class DummyResp:
        def raise_for_status(self): ...

        def json(self):
            return {"message": {"content": "hello world"}}

    def fake_post(url, json, timeout):
        return DummyResp()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)

    out = llm_module.generate_explanation({}, {}, [])
    assert out == "hello world"


def test_api_process_end_to_end(monkeypatch):
    sample_text = "Electric Cons.: 50 kWh\nDate: 2024-01-01"

    # Patch dependencies to isolate from external services and heavy OCR/LLM.
    monkeypatch.setattr("app.main.extract_text_from_file", lambda _: sample_text)
    monkeypatch.setattr("app.main.store_document", lambda fields, emissions: "doc-1")
    monkeypatch.setattr("app.main.get_history", lambda limit=12: [])
    monkeypatch.setattr("app.main.forecast_next_month", lambda history: {"predicted_kgco2": 1.0})
    monkeypatch.setattr("app.main.generate_explanation", lambda f, e, h: "ok")

    client = TestClient(app)
    fake_image = io.BytesIO(b"fakeimagebytes")
    files = {"file": ("test.png", fake_image, "image/png")}
    resp = client.post("/process", files=files)
    assert resp.status_code == 200
    data = resp.json()
    for key in ["raw_text", "fields", "emissions", "history", "forecast", "explanation"]:
        assert key in data

