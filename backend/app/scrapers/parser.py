import re
from typing import List, Dict, Any, Optional

# List of Indian states and Union Territories for state extraction matching
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
    "Chandigarh", "Dadra and Nagar Haveli", "Daman and Diu", "Delhi", "Jammu and Kashmir", 
    "Ladakh", "Lakshadweep", "Puducherry"
]

# Lowercase mapping for matching
STATES_LOWER = {s.lower(): s for s in INDIAN_STATES}

# Common state abbreviations mapping
STATE_ABBR_MAP = {
    "ap": "Andhra Pradesh", "ar": "Arunachal Pradesh", "as": "Assam", "br": "Bihar",
    "cg": "Chhattisgarh", "ga": "Goa", "gj": "Gujarat", "hr": "Haryana", "hp": "Himachal Pradesh",
    "jh": "Jharkhand", "ka": "Karnataka", "kl": "Kerala", "mp": "Madhya Pradesh", "mh": "Maharashtra",
    "mn": "Manipur", "ml": "Meghalaya", "mz": "Mizoram", "nl": "Nagaland", "od": "Odisha", "or": "Odisha",
    "pb": "Punjab", "rj": "Rajasthan", "sk": "Sikkim", "tn": "Tamil Nadu", "tg": "Telangana", "ts": "Telangana",
    "tr": "Tripura", "up": "Uttar Pradesh", "uk": "Uttarakhand", "ua": "Uttarakhand", "wb": "West Bengal",
    "dl": "Delhi", "jk": "Jammu and Kashmir", "py": "Puducherry", "ch": "Chandigarh"
}

def clean_whitespace(text: Optional[str]) -> str:
    """
    Cleans up redundant whitespaces, tabs, newlines.
    """
    if not text:
        return ""
    # Replace multiple spaces/newlines/tabs with a single space
    cleaned = re.sub(r'\s+', ' ', text)
    return cleaned.strip()

def clean_address(address: Optional[str]) -> str:
    """
    Cleans address strings, removes excess commas, formatting characters.
    """
    if not address:
        return ""
    cleaned = clean_whitespace(address)
    # Remove leading/trailing commas and redundant symbols
    cleaned = re.sub(r'^[\s,]+|[\s,]+$', '', cleaned)
    cleaned = re.sub(r',(\s*,)+', ',', cleaned) # remove duplicate commas
    return cleaned

def extract_pincode(text: Optional[str]) -> Optional[str]:
    """
    Extracts a 6-digit Indian PIN code from text.
    Matches formats like 400001, 400 001, or Pin-400001.
    """
    if not text:
        return None
    # Look for 6 consecutive digits or 3 digits followed by an optional space and 3 digits
    pin_match = re.search(r'\b\d{6}\b', text)
    if pin_match:
        return pin_match.group(0)
    
    # Check for space separated pin like 400 001
    space_pin_match = re.search(r'\b(\d{3})\s+(\d{3})\b', text)
    if space_pin_match:
        return f"{space_pin_match.group(1)}{space_pin_match.group(2)}"
        
    return None

def extract_state(text: Optional[str]) -> Optional[str]:
    """
    Extracts Indian state name from text by checking full name or abbreviation matches.
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Try exact match for state names
    for state_l, state_name in STATES_LOWER.items():
        # Match using word boundaries to avoid partial matching (e.g. "Goa" in "Goaldih")
        if re.search(r'\b' + re.escape(state_l) + r'\b', text_lower):
            return state_name
            
    # Try match for abbreviations
    for abbr, state_name in STATE_ABBR_MAP.items():
        if re.search(r'\b' + re.escape(abbr) + r'\b', text_lower):
            return state_name
            
    return None

def extract_city(address: Optional[str], fallback_state: Optional[str] = None) -> Optional[str]:
    """
    Attempts to parse city from address.
    Commonly, the city resides before the state and pin code near the end of the address.
    """
    if not address:
        return None
    
    cleaned = clean_address(address)
    # Tokenize the address by commas
    parts = [p.strip() for p in cleaned.split(",")]
    if len(parts) < 2:
        return None
        
    # Standard Indian cities list search fallback or scanning the last 2-3 tokens
    # Typically address ends like: ..., City, State - PIN
    # Let's inspect the last few parts
    for part in reversed(parts):
        # Skip if it is just a pincode
        if extract_pincode(part) == part or part.isdigit():
            continue
        # Skip if it matches a state name or abbreviation
        if extract_state(part):
            continue
        # Check if the part is a single word or short name, which is likely the city
        words = part.split()
        if len(words) > 0 and len(words) <= 3:
            # Clean up number strings or street names
            if not any(char.isdigit() for char in part):
                return part
                
    return None

def normalize_phone(phone_str: Optional[str]) -> Optional[str]:
    """
    Normalizes phone numbers, extracts digits, retains country code prefix if valid (+91).
    """
    if not phone_str:
        return None
    
    # Remove all whitespace, parentheses, and dashes
    cleaned = re.sub(r'[\s\(\)\-\[\]]', '', phone_str)
    
    # Extract digits and leading plus
    digits = re.sub(r'[^\d+]', '', cleaned)
    
    if not digits:
        return None
        
    # Standardize Indian mobile/landline numbers (+91)
    if digits.startswith("+91"):
        if len(digits) == 13: # +91 + 10 digits
            return digits
    elif digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    elif digits.startswith("0") and len(digits) == 11: # 0 + 10 digits
        return f"+91{digits[1:]}"
    elif len(digits) == 10:
        return f"+91{digits}"
        
    return digits # return whatever digits found as fallback

def is_duplicate(d1: Dict[str, Any], d2: Dict[str, Any]) -> bool:
    """
    Helper to identify duplicate dealer records.
    Considers records duplicates if they share identical normalized phone numbers,
    or have high overlap of Name + Address pincodes.
    """
    # 1. Compare normalized phone numbers
    p1 = normalize_phone(d1.get("phone"))
    p2 = normalize_phone(d2.get("phone"))
    if p1 and p2 and p1 == p2:
        return True
        
    # 2. Compare Name and Address pincode
    name1 = clean_whitespace(d1.get("dealer_name")).lower()
    name2 = clean_whitespace(d2.get("dealer_name")).lower()
    pin1 = extract_pincode(d1.get("address")) or d1.get("pincode")
    pin2 = extract_pincode(d2.get("address")) or d2.get("pincode")
    
    if name1 == name2 and pin1 and pin2 and pin1 == pin2:
        return True
        
    return False
