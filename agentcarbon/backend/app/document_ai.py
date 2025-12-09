# document_ai.py

import re
from datetime import datetime
from typing import Dict, Optional


def _num(pattern: str, text: str) -> Optional[float]:
    m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _find_first_match(patterns, text: str):
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            return m
    return None


def extract_fields(raw_text: str, image_bytes: bytes | None = None) -> Dict:
    """
    Current implementation: regex-only, robust version.
    (LayoutLM can be added later; for now image_bytes is ignored.)
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    text = raw_text

    fields: Dict = {
        "energy_kwh": None,
        "water_gallons": None,
        "gas_therms": None,
        "fuel_liters": None,
        "distance_km": None,
        "vendor": None,
        "date": None,
    }

    # --- quantities ---
    fields["energy_kwh"] = _num(
        r"(?:electric(?:ity)?(?:\s+usage)?[:\s]+)(\d+(?:\.\d+)?)\s*kwh", text
    ) or _num(r"(\d+(?:\.\d+)?)\s*kwh", text)

    fields["water_gallons"] = _num(
        r"(?:water(?:\s+usage)?[:\s]+)(\d+(?:\.\d+)?)\s*(?:gallons?|gal)", text
    )

    fields["gas_therms"] = _num(
        r"(?:gas|natural\s+gas)[:\s]+(\d+(?:\.\d+)?)\s*(?:therms?|th)", text
    )

    fields["fuel_liters"] = _num(
        r"(?:diesel|petrol|fuel)[:\s]+(\d+(?:\.\d+)?)\s*(?:l|liters?)", text
    )

    fields["distance_km"] = _num(
        r"(?:distance|flight|travel)[:\s]+(\d+(?:\.\d+)?)\s*km", text
    )

    # --- vendor ---
    candidate_vendor = None
    for l in lines[:10]:
        if "[YOUR COMPANY" in l or "Template.net" in l:
            continue
        if l.lower().startswith(("bill to", "invoice", "utility bill")):
            continue
        if "@" in l or "." in l:
            candidate_vendor = l
            break
    if not candidate_vendor:
        for l in lines:
            if "[YOUR COMPANY" in l or "Template.net" in l:
                continue
            if l.lower().startswith(("bill to", "invoice", "utility bill")):
                continue
            candidate_vendor = l
            break
    fields["vendor"] = candidate_vendor

    # --- date ---
    m = _find_first_match(
        [
            r"invoice\s+date[:\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
            r"invoice\s+date[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})",
            r"date[:\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
            r"date[:\s]+(\d{1,2}-\d{1,2}-\d{2,4})",
        ],
        text,
    )

    parsed_date = None
    if m:
        date_str = m.group(1).strip()
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"):
            try:
                parsed_date = datetime.strptime(date_str, fmt).date().isoformat()
                break
            except ValueError:
                continue
        if not parsed_date:
            parsed_date = date_str

    fields["date"] = parsed_date
    return fields
