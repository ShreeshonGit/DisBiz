import json
import re
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

def find_dealers_in_json(data: Any) -> Optional[List[Dict[str, Any]]]:
    """
    Recursively searches JSON for lists of objects containing dealer signatures.
    """
    if isinstance(data, list):
        candidate_list = []
        for item in data:
            if isinstance(item, dict):
                score = 0
                keys = {k.lower() for k in item.keys()}
                name_keys = {"name", "title", "store", "dealer", "outlet", "shop", "branch", "partner"}
                addr_keys = {"address", "addr", "street", "location", "formatted_address", "address1", "address2"}
                phone_keys = {"phone", "tel", "mobile", "contact", "phone1", "telephone"}
                coord_keys = {"lat", "latitude", "lng", "longitude", "coordinates", "coords"}
                
                has_name = False
                for nk in name_keys:
                    if nk in keys:
                        has_name = True
                        break
                    for k in keys:
                        if nk in k:
                            has_name = True
                            break
                    if has_name:
                        break
                if has_name:
                    score += 2
                    
                has_addr = False
                for ak in addr_keys:
                    if ak in keys:
                        has_addr = True
                        break
                    for k in keys:
                        if ak in k:
                            has_addr = True
                            break
                    if has_addr:
                        break
                if has_addr:
                    score += 2
                    
                has_phone = False
                for pk in phone_keys:
                    if pk in keys:
                        has_phone = True
                        break
                    for k in keys:
                        if pk in k:
                            has_phone = True
                            break
                    if has_phone:
                        break
                if has_phone:
                    score += 1
                    
                has_coord = False
                for ck in coord_keys:
                    if ck in keys:
                        has_coord = True
                        break
                    for k in keys:
                        if ck in k:
                            has_coord = True
                            break
                    if has_coord:
                        break
                if has_coord:
                    score += 1
                    
                if score >= 3:
                    candidate_list.append(item)
                    
        if len(candidate_list) > 0:
            return candidate_list
            
        for item in data:
            res = find_dealers_in_json(item)
            if res:
                return res
                
    elif isinstance(data, dict):
        for k, v in data.items():
            res = find_dealers_in_json(v)
            if res:
                return res
                
    return None

def parse_dealers_from_json_list(json_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed_dealers = []
    for item in json_list:
        keys = {k.lower(): k for k in item.keys()}
        
        def get_val(patterns: List[str], default="") -> Any:
            for p in patterns:
                for kl, k in keys.items():
                    if p == kl or p in kl:
                        val = item[k]
                        if not isinstance(val, (dict, list)):
                            return val
            return default

        dealer_name = get_val(["name", "title", "store", "dealer", "outlet", "shop", "branch"])
        address = get_val(["address", "addr", "street", "location", "formatted_address"])
        city = get_val(["city", "town", "district"])
        state = get_val(["state", "region", "province"])
        pincode = get_val(["pincode", "zip", "postal", "pin"])
        phone = get_val(["phone", "tel", "mobile", "contact"])
        email = get_val(["email", "mail"])
        website = get_val(["website", "web", "url", "link"])
        latitude = get_val(["latitude", "lat"])
        longitude = get_val(["longitude", "lng", "lon"])
        
        lat_val = None
        lon_val = None
        
        map_link = get_val(["map", "google_map", "gps"])
        if map_link and isinstance(map_link, str) and "," in map_link:
            parts = map_link.split(",")
            if len(parts) == 2:
                try:
                    lat_val = float(parts[0].strip())
                    lon_val = float(parts[1].strip())
                except ValueError:
                    pass
                    
        if latitude is not None and str(latitude).strip():
            try:
                lat_val = float(str(latitude).strip())
            except ValueError:
                pass
        if longitude is not None and str(longitude).strip():
            try:
                lon_val = float(str(longitude).strip())
            except ValueError:
                pass

        addr_str = str(address) if address else ""
        city_str = str(city) if city else ""
        state_str = str(state) if state else ""
        if addr_str and (not city_str or not state_str):
            parts = [p.strip() for p in addr_str.split(",")]
            if len(parts) >= 3:
                if not city_str:
                    city_str = parts[-2]
                if not state_str:
                    state_str = parts[-1]

        extra_fields = {}
        standard_keys = {
            "name", "title", "store", "dealer", "outlet", "shop", "branch",
            "address", "addr", "street", "location", "formatted_address",
            "city", "town", "state", "region", "province", "pincode", "zip", "postal", "pin",
            "phone", "tel", "mobile", "contact", "email", "mail", "website", "web", "url", "link",
            "latitude", "lat", "longitude", "lng", "lon"
        }
        for k, v in item.items():
            k_lower = k.lower()
            if k_lower not in standard_keys and not any(sk in k_lower for sk in standard_keys):
                extra_fields[k] = v

        parsed_dealers.append({
            "dealer_name": str(dealer_name).strip() if dealer_name else "",
            "address": addr_str.strip(),
            "city": city_str.strip(),
            "state": state_str.strip(),
            "pincode": str(pincode).strip() if pincode else "",
            "phone": str(phone).strip() if phone else "",
            "email": str(email).strip() if email else "",
            "website": str(website).strip() if website else "",
            "latitude": lat_val,
            "longitude": lon_val,
            "extra_fields": extra_fields
        })
    return parsed_dealers

def parse_html_dealers(html_content: str, selectors: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Normalize selectors
    norm_selectors = {}
    for k, v in selectors.items():
        if isinstance(v, str):
            norm_selectors[k] = {"selector": v}
        elif isinstance(v, dict):
            norm_selectors[k] = v
        elif isinstance(v, list):
            norm_selectors[k] = {"selector": v[0] if v else ""}
            
    soup = BeautifulSoup(html_content, "lxml")
    container_sel = norm_selectors.get("container", {}).get("selector")
    if not container_sel:
        return []
        
    containers = soup.select(container_sel)
    parsed = []
    
    for node in containers:
        def get_field_text(field_name: str) -> str:
            sel_info = norm_selectors.get(field_name, {})
            sel = sel_info.get("selector")
            if sel:
                target = node.select_one(sel)
                if target:
                    if target.name == "input":
                        return target.get("value", "").strip()
                    if field_name == "latitude" and target.get("data-lat"):
                        return target.get("data-lat", "").strip()
                    if field_name == "latitude" and target.get("data-latitude"):
                        return target.get("data-latitude", "").strip()
                    if field_name == "longitude" and target.get("data-lng"):
                        return target.get("data-lng", "").strip()
                    if field_name == "longitude" and target.get("data-longitude"):
                        return target.get("data-longitude", "").strip()
                        
                    if field_name == "website" and target.name == "a":
                        return target.get("href", "").strip()
                    elif field_name == "phone" and target.name == "a" and target.get("href", "").startswith("tel:"):
                        return target.get("href", "")[4:].strip()
                    elif field_name == "email" and target.name == "a" and target.get("href", "").startswith("mailto:"):
                        return target.get("href", "")[7:].strip()
                    return target.get_text().strip()
            return ""

        dealer_name = get_field_text("name")
        address = get_field_text("address")
        city = get_field_text("city")
        state = get_field_text("state")
        pincode = get_field_text("pincode")
        phone = get_field_text("phone")
        email = get_field_text("email")
        website = get_field_text("website")
        latitude = get_field_text("latitude")
        longitude = get_field_text("longitude")
        
        if not dealer_name and not address:
            continue
            
        lat_val = float(latitude) if latitude and re.match(r'^-?\d+(\.\d+)?$', latitude) else None
        if lat_val is None:
            lat_attr = node.get("data-lat") or node.get("data-latitude")
            if lat_attr:
                try: lat_val = float(str(lat_attr).strip())
                except ValueError: pass
                
        lon_val = float(longitude) if longitude and re.match(r'^-?\d+(\.\d+)?$', longitude) else None
        if lon_val is None:
            lon_attr = node.get("data-lng") or node.get("data-longitude")
            if lon_attr:
                try: lon_val = float(str(lon_attr).strip())
                except ValueError: pass

        parsed.append({
            "dealer_name": dealer_name,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "phone": phone,
            "email": email,
            "website": website,
            "latitude": lat_val,
            "longitude": lon_val
        })
    return parsed

def safe_json_load(res: Any) -> Any:
    """
    Safely deserializes JSON from a response object, handling either a dict,
    a JSON string, or AsyncMock issues.
    """
    try:
        if hasattr(res, "text") and isinstance(res.text, str):
            return json.loads(res.text)
        val = res.json()
        if asyncio.iscoroutine(val):
            if hasattr(res, "text") and isinstance(res.text, str):
                return json.loads(res.text)
        return val
    except Exception:
        if isinstance(res, dict):
            return res
        return {}
