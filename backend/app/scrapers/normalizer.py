from typing import Dict, Any, Optional
from app.scrapers.parser import (
    clean_whitespace,
    clean_address,
    normalize_phone,
    extract_pincode,
    extract_state,
    extract_city
)

def normalize_dealer(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies the normalization pipeline to a single raw dealer record.
    Converts and standardizes all fields.
    """
    normalized = {}

    # 1. Normalize Dealer Name (Title case and trim whitespace)
    raw_name = raw_data.get("dealer_name") or raw_data.get("name") or ""
    normalized["dealer_name"] = clean_whitespace(str(raw_name)).title()

    # 2. Normalize Address
    raw_address = raw_data.get("address") or ""
    normalized["address"] = clean_address(str(raw_address))

    # 3. Pincode (Extract from address if not explicitly present)
    pincode = raw_data.get("pincode") or extract_pincode(normalized["address"])
    normalized["pincode"] = clean_whitespace(str(pincode)) if pincode else ""

    # 4. State (Extract or clean up)
    raw_state = raw_data.get("state") or extract_state(normalized["address"])
    state = extract_state(str(raw_state)) if raw_state else None
    normalized["state"] = state if state else (clean_whitespace(str(raw_state)).title() if raw_state else "")

    # 5. City (Extract or clean up)
    raw_city = raw_data.get("city") or extract_city(normalized["address"])
    city = clean_whitespace(str(raw_city)).title() if raw_city else ""
    # Strip any digits/special characters from city name if extracted poorly
    city = "".join([c for c in city if not c.isdigit()]).strip()
    normalized["city"] = city

    # 6. Phone number normalization
    phone = raw_data.get("phone") or raw_data.get("telephone") or ""
    normalized["phone"] = normalize_phone(str(phone)) if phone else None

    # 7. Email normalization (lowercase and strip)
    email = raw_data.get("email") or ""
    normalized["email"] = clean_whitespace(str(email)).lower() if email else None

    # 8. Web link normalization
    website = raw_data.get("website") or raw_data.get("url") or ""
    normalized["website"] = clean_whitespace(str(website)).lower() if website else None

    # 9. Coordinates (Parse floats safely)
    for field in ["latitude", "longitude"]:
        val = raw_data.get(field)
        if val is not None:
            try:
                normalized[field] = float(val)
            except (ValueError, TypeError):
                normalized[field] = None
        else:
            normalized[field] = None

    return normalized
