import sys
sys.path.insert(0, ".")
from app.scrapers.selector_discovery import SelectorDiscovery
from app.scrapers.generic_scraper import parse_html_dealers
import json

def main():
    with open("scratch/bosch_debug/bosch_final_dom.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    disc = SelectorDiscovery.discover_selectors(html)
    print("Discovered Selectors:")
    print(json.dumps(disc, indent=2))
    
    # Convert discovered format to plain selector dict
    selectors = {k: v.get("selector") if isinstance(v, dict) else v for k, v in disc.items()}
    
    parsed = parse_html_dealers(html, selectors)
    print(f"\nParsed dealer count with discovered selectors: {len(parsed)}")
    
    for i, p in enumerate(parsed[:3]):
        print(f"  Parsed {i+1}: {p}")

if __name__ == "__main__":
    main()
