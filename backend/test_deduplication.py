import sys
import unittest

sys.path.insert(0, ".")

from app.scrapers.dealer_deduplicator import DealerDeduplicator

class TestDealerDeduplicator(unittest.TestCase):
    def test_exact_email_match(self):
        """Verify duplicate classification on matching emails."""
        d1 = {"dealer_name": "Shop A", "email": "test@shop.com"}
        d2 = {"dealer_name": "Shop B", "email": "test@shop.com"}
        self.assertTrue(DealerDeduplicator.is_duplicate(d1, d2))

    def test_phone_normalization_match(self):
        """Verify duplicate classification on phone numbers after digit normalization."""
        d1 = {"dealer_name": "Store X", "phone": "+91 98765 43210"}
        d2 = {"dealer_name": "Store Y", "phone": "09876543210"}
        self.assertTrue(DealerDeduplicator.is_duplicate(d1, d2))

    def test_gps_proximity_match(self):
        """Verify duplicate classification when coordinates lie within ~10 meters limit."""
        d1 = {"dealer_name": "Outlet A", "latitude": 28.6139, "longitude": 77.2090}
        d2 = {"dealer_name": "Outlet B", "latitude": 28.61392, "longitude": 77.20902} # Very close proximity
        self.assertTrue(DealerDeduplicator.is_duplicate(d1, d2))

    def test_fuzzy_name_address_overlap(self):
        """Verify duplicate classification on high token similarity of names and addresses."""
        d1 = {
            "dealer_name": "Lava Care Secunderabad", 
            "address": "RP Road, near Metro Station, Secunderabad, Telangana 500003"
        }
        d2 = {
            "dealer_name": "Lava Care Express - Secunderabad", 
            "address": "RP Road, Secunderabad 500003"
        }
        self.assertTrue(DealerDeduplicator.is_duplicate(d1, d2))

    def test_non_duplicate(self):
        """Verify unique classification for different dealer entities."""
        d1 = {
            "dealer_name": "Lava Care Secunderabad", 
            "address": "RP Road, Secunderabad, Telangana 500003"
        }
        d2 = {
            "dealer_name": "Nokia Care Kolkata", 
            "address": "Salt Lake City Sector 5, Kolkata, West Bengal 700091"
        }
        self.assertFalse(DealerDeduplicator.is_duplicate(d1, d2))

if __name__ == "__main__":
    unittest.main()
