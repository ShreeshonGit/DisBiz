import sys
import asyncio
from uuid import uuid4
import time
import logging

sys.path.insert(0, ".")

from app.scrapers.generic_scraper import GenericScraper

logging.basicConfig(level=logging.INFO)

TARGET_LOCATORS = [
    {
        "name": "Lava Mobiles",
        "url": "https://www.lavamobiles.com/lavastoredealer",
        "expected_type": "API"
    },
    {
        "name": "Sleepwell",
        "url": "https://sleepwellmypartner.com/",
        "expected_type": "HTML/Mock"
    },
    {
        "name": "Titan Watches (India)",
        "url": "https://www.titan.co.in/store-locator",
        "expected_type": "HTML/JS"
    },
    {
        "name": "Milton Homeware (India)",
        "url": "https://www.milton.in/pages/store-locator",
        "expected_type": "HTML/JS"
    },
    {
        "name": "Xiaomi India Mi Home",
        "url": "https://www.mi.com/in/service/mihome",
        "expected_type": "HTML/JS"
    }
]

async def verify_locator(locator):
    print("=" * 60)
    print(f"TESTING LOCATOR: {locator['name']}")
    print(f"URL: {locator['url']}")
    print("=" * 60)
    
    brand_id = uuid4()
    scraper = GenericScraper(
        brand_id=brand_id,
        brand_name=locator["name"],
        locator_url=locator["url"],
        config={"max_pages": 1}  # Short run limit
    )
    
    start_time = time.time()
    dealers = []
    try:
        dealers = await scraper.extract_dealers()
    except Exception as e:
        print(f"Execution crashed: {e}")
        
    duration = time.time() - start_time
    
    print("\nLogs captured:")
    for log in scraper.logs:
        print(f"  {log}")
        
    print("-" * 60)
    print(f"RESULT SUMMARY FOR {locator['name']}:")
    print(f"  Total records parsed: {len(dealers)}")
    print(f"  Execution time: {duration:.2f}s")
    if dealers:
        print(f"  Sample Record Name: {dealers[0].get('dealer_name')}")
        print(f"  Sample Record Phone: {dealers[0].get('phone')}")
        print(f"  Sample Record Lat/Lng: {dealers[0].get('latitude')}, {dealers[0].get('longitude')}")
    print("=" * 60 + "\n")
    
    strategy = "PLAYWRIGHT"
    api_detected = False
    for log in scraper.logs:
        if "API endpoint detected" in log or "JSON API payload detected" in log:
            api_detected = True
            strategy = "API"
        elif "Static HTML matching selectors" in log:
            strategy = "STATIC_HTML"
            
    return {
        "name": locator["name"],
        "url": locator["url"],
        "records": len(dealers),
        "duration": duration,
        "strategy": strategy,
        "api_detected": api_detected,
        "sample": dealers[0] if dealers else None
    }

async def main():
    print("Starting Universal Scraper validation benchmark...\n")
    results = []
    for loc in TARGET_LOCATORS:
        res = await verify_locator(loc)
        results.append(res)
        
    print("\n" + "#" * 60)
    print("FINAL BENCHMARK SUMMARY TABLE")
    print("#" * 60)
    print(f"{'Locator Name':<25} | {'Records':<8} | {'Duration (s)':<12} | {'Strategy':<12}")
    print("-" * 65)
    for r in results:
        print(f"{r['name']:<25} | {r['records']:<8} | {r['duration']:<12.2f} | {r['strategy']:<12}")
    print("#" * 60)

if __name__ == "__main__":
    asyncio.run(main())
