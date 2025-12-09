from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import numpy as np
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (final_year_project/.env)
# rag.py is at: final_year_project/agentcarbon/backend/app/rag.py
# Go up 4 levels: rag.py -> app -> backend -> agentcarbon -> final_year_project (root)
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

QDRANT_URL = os.getenv("QDRANT_URL")          # e.g. https://xxxxxx.us-east-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # from Qdrant Cloud dashboard
COLLECTION = "agentcarbon_docs"

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set in .env for cloud usage.")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def _ensure_collection() -> None:
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    if COLLECTION not in names:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=3, distance=Distance.COSINE),
        )


def _make_vector(fields: dict, emissions: dict) -> np.ndarray:
    kwh = float(fields.get("energy_kwh") or 0.0)
    water = float(fields.get("water_gallons") or 0.0)
    total = float(emissions.get("total_kgco2") or 0.0)
    return np.array([kwh, water, total], dtype=float)


def store_document(fields: dict, emissions: dict) -> str:
    _ensure_collection()
    vec = _make_vector(fields, emissions)
    doc_id = str(uuid.uuid4())
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=doc_id,
                vector=vec.tolist(),
                payload={"fields": fields, "emissions": emissions},
            )
        ],
    )
    return doc_id


def get_history(limit: int = 12) -> List[Dict]:
    _ensure_collection()
    points, _ = client.scroll(
        collection_name=COLLECTION,
        limit=limit,
        with_payload=True,
    )
    history: List[Dict] = []
    for p in points:
        history.append(
            {
                "fields": p.payload.get("fields", {}),
                "emissions": p.payload.get("emissions", {}),
            }
        )
    return history
