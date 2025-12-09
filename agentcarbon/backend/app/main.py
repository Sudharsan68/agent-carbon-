from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ocr import extract_text_from_file
from .document_ai import extract_fields
from .calculator import compute_emissions
from .rag import store_document, get_history
from .predictor import forecast_next_month
from .llm import generate_explanation   # ← NEW

app = FastAPI(title="AgentCarbon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmissionResponse(BaseModel):
    raw_text: str
    fields: dict
    emissions: dict
    history: list
    forecast: dict
    explanation: str | None = None   # ← NEW

@app.get("/v1/models")
async def get_models():
    """Handle OpenAI-compatible /v1/models endpoint to reduce 404 noise."""
    return {"data": []}

@app.post("/process", response_model=EmissionResponse)
async def process_document(file: UploadFile = File(...)):
    # 1. Read file once
    content = await file.read()

    # 2. OCR
    try:
        raw_text = extract_text_from_file(content)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # 3. Document understanding (regex-based for now)
    fields = extract_fields(raw_text)   # no image_bytes

    # 4. Emission calculation
    emissions = compute_emissions(fields)

    # 5. Store in RAG / history
    _ = store_document(fields, emissions)

    # 6. Retrieve history + forecast
    history = get_history(limit=12)
    forecast = forecast_next_month(history)

    # 7. LLM explanation (Ollama Llama 3)
    explanation = generate_explanation(fields, emissions, history)

    return EmissionResponse(
        raw_text=raw_text,
        fields=fields,
        emissions=emissions,
        history=history,
        forecast=forecast,
        explanation=explanation,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
