# app/llm.py
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3"

SYSTEM_PROMPT = (
    "You are AgentCarbon, an expert sustainability assistant. "
    "You receive extracted invoice fields and carbon emissions. "
    "Explain the results in simple English and give 2–3 specific, practical "
    "suggestions to reduce emissions. Do not change any numeric values."
)

def generate_explanation(fields: dict, emissions: dict, history: list) -> str:
    user_msg = (
        f"Current fields: {fields}\n"
        f"Current emissions: {emissions}\n"
        f"Past records (may be empty): {history}\n\n"
        "1) Briefly summarize this bill's emissions.\n"
        "2) Mention if emissions seem higher or lower than usual based on history.\n"
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

    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"].strip()
