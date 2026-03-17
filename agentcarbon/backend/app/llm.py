# app/llm.py
import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/chat")
MODEL_NAME = "llama3.2-vision:11b"

SYSTEM_PROMPT = (
    "You are AgentCarbon, an expert sustainability assistant. "
    "You receive extracted invoice fields and carbon emissions. "
    "Explain the results in simple English and give 2–3 specific, practical "
    "suggestions to reduce emissions. Do not change any numeric values. "
    "Output EXTREMELY CLEAN PLAIN TEXT ONLY. Do not use asterisks (**), bolding, or markdown formatting."
)


def generate_explanation(
    fields: dict, 
    emissions: dict, 
    history: list, 
    ml_predicted_co2: float | None = None
) -> str | None:
    
    calculated_co2 = emissions.get("total_kgco2", "N/A")
    
    ml_context = ""
    if ml_predicted_co2 is not None:
        ml_context = (
            f"The calculated emissions are {calculated_co2}, but the ML model suggests {ml_predicted_co2}. "
            "Briefly explain why there might be a difference (e.g., seasonal factors or typical consumption patterns for this facility). "
        )

    user_msg = (
        f"Current fields: {fields}\n"
        f"Current emissions: {emissions}\n"
        f"ML Predicted CO2: {ml_predicted_co2}\n"
        f"Past records (may be empty): {history}\n\n"
        "1) Briefly summarize this bill's emissions.\n"
        "2) Mention if emissions seem higher or lower than usual based on history.\n"
        f"{ml_context}\n"
        "3) Give 2–3 concrete tips to reduce future emissions."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
    }

    try:
        # No timeout argument -> waits indefinitely until Ollama responds
        resp = requests.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"].strip()
    except Exception as exc:
        print(f"❌ LLM Error: {exc}")
        return None
