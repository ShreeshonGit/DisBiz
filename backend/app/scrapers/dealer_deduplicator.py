import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DealerDeduplicator:
    """
    Deduplication module that implements exact match rules (emails, phone numbers,
    GPS coordinates) and fuzzy string similarity heuristics on dealer names and addresses.
    """

    @staticmethod
    def clean_phone(phone: str) -> str:
        """Removes all non-digit characters from phone number."""
        if not phone:
            return ""
        return re.sub(r'\D', '', phone)

    @staticmethod
    def token_similarity(s1: str, s2: str) -> float:
        """
        Computes the Jaccard similarity of word token sets for two strings.
        Useful for address and name comparison.
        """
        if not s1 or not s2:
            return 0.0
        
        words1 = set(re.findall(r'\w+', s1.lower()))
        words2 = set(re.findall(r'\w+', s2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    @classmethod
    def is_duplicate(cls, d1: Dict[str, Any], d2: Dict[str, Any]) -> bool:
        """
        Compares two dealers and returns True if they are classified as duplicates.
        """
        # 1. Compare Email if present in both
        e1 = str(d1.get("email") or "").strip().lower()
        e2 = str(d2.get("email") or "").strip().lower()
        if e1 and e2 and e1 == e2:
            return True

        # 2. Compare Phone if present in both (using normalized digits)
        p1 = cls.clean_phone(d1.get("phone") or "")
        p2 = cls.clean_phone(d2.get("phone") or "")
        # Require phone to be at least 10 digits for matching
        if p1 and p2 and len(p1) >= 10 and len(p2) >= 10 and p1[-10:] == p2[-10:]:
            return True

        # 3. Compare Coordinates if present in both
        lat1, lon1 = d1.get("latitude"), d1.get("longitude")
        lat2, lon2 = d2.get("latitude"), d2.get("longitude")
        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            try:
                # Proximity check within ~10 meters (roughly 0.0001 degrees)
                if abs(float(lat1) - float(lat2)) < 0.0001 and abs(float(lon1) - float(lon2)) < 0.0001:
                    return True
            except (ValueError, TypeError):
                pass

        # 4. Compare Name and Address token similarity
        n1 = str(d1.get("dealer_name") or "").strip()
        n2 = str(d2.get("dealer_name") or "").strip()
        a1 = str(d1.get("address") or "").strip()
        a2 = str(d2.get("address") or "").strip()

        name_sim = cls.token_similarity(n1, n2)
        addr_sim = cls.token_similarity(a1, a2)

        # High name similarity AND high address similarity
        if name_sim >= 0.7 and addr_sim >= 0.5:
            return True

        # Exact name match with moderate address similarity
        if n1.lower() == n2.lower() and addr_sim >= 0.5:
            return True

        return False

    @classmethod
    def filter_duplicates(cls, incoming_dealers: List[Dict[str, Any]], existing_dealers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters out duplicate records from incoming list by comparing against existing list.
        Also deduplicates the incoming list against itself.
        """
        unique_incoming = []
        
        for inc in incoming_dealers:
            # Check against already added incoming
            is_dup = False
            for added in unique_incoming:
                if cls.is_duplicate(inc, added):
                    is_dup = True
                    break
            
            if is_dup:
                continue
                
            # Check against database existing dealers
            for ext in existing_dealers:
                if cls.is_duplicate(inc, ext):
                    is_dup = True
                    break
                    
            if not is_dup:
                unique_incoming.append(inc)
                
        return unique_incoming
