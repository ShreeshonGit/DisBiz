from typing import Dict, Any, List, Tuple
import re

def validate_dealer(dealer_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a normalized dealer record.
    Returns:
        is_valid (bool): True if record meets quality standards, False otherwise.
        errors (List[str]): List of validation error messages.
    """
    errors = []

    # 1. Validate Dealer Name (Required)
    name = dealer_data.get("dealer_name")
    if not name or not name.strip():
        errors.append("Dealer name is missing or empty.")

    # 2. Validate Address (Required)
    address = dealer_data.get("address")
    if not address or not address.strip():
        errors.append("Address is missing or empty.")

    # 3. Validate PIN Code (Required, must be exactly 6 digits)
    pincode = dealer_data.get("pincode")
    if not pincode:
        errors.append("PIN code is missing.")
    else:
        # Check if it consists of exactly 6 digits
        if not re.match(r'^\d{6}$', pincode):
            errors.append(f"PIN code '{pincode}' is invalid. Must be exactly 6 digits.")

    # 4. Validate Coordinates (Optional, but must have valid bounds if present)
    lat = dealer_data.get("latitude")
    lng = dealer_data.get("longitude")
    
    if lat is not None:
        if lat < -90.0 or lat > 90.0:
            errors.append(f"Latitude '{lat}' is out of range (-90 to 90).")
            
    if lng is not None:
        if lng < -180.0 or lng > 180.0:
            errors.append(f"Longitude '{lng}' is out of range (-180 to 180).")

    # 5. Validate Phone (Optional, but if present must be at least 10 digits long)
    phone = dealer_data.get("phone")
    if phone:
        # Strip out country code symbol
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            errors.append(f"Phone number '{phone}' is too short. Must contain at least 10 digits.")

    return len(errors) == 0, errors


def calculate_quality_score(dealer_data: Dict[str, Any]) -> int:
    """
    Computes a data quality score (0 to 100) based on fields present:
    Dealer Name: +20
    Address: +20
    Phone: +20
    City: +10
    State: +10
    PIN: +10
    Coordinates: +5
    Website: +5
    """
    score = 0
    
    # 1. Dealer Name (+20)
    if dealer_data.get("dealer_name") and str(dealer_data["dealer_name"]).strip():
        score += 20
        
    # 2. Address (+20)
    if dealer_data.get("address") and str(dealer_data["address"]).strip():
        score += 20
        
    # 3. Phone (+20)
    if dealer_data.get("phone") and str(dealer_data["phone"]).strip():
        # Clean and ensure it has digits
        digits = re.sub(r'\D', '', str(dealer_data["phone"]))
        if len(digits) >= 10:
            score += 20
        else:
            score += 10 # Some phone text present but incomplete
        
    # 4. City (+10)
    if dealer_data.get("city") and str(dealer_data["city"]).strip():
        score += 10
        
    # 5. State (+10)
    if dealer_data.get("state") and str(dealer_data["state"]).strip():
        score += 10
        
    # 6. PIN (+10)
    pin = dealer_data.get("pincode")
    if pin and re.match(r'^\d{6}$', str(pin).strip()):
        score += 10
        
    # 7. Coordinates (+5)
    lat = dealer_data.get("latitude")
    lng = dealer_data.get("longitude")
    if lat is not None and lng is not None:
        try:
            if -90.0 <= float(lat) <= 90.0 and -180.0 <= float(lng) <= 180.0:
                score += 5
        except (ValueError, TypeError):
            pass
            
    # 8. Website (+5)
    if dealer_data.get("website") and str(dealer_data["website"]).strip():
        score += 5
        
    return score
