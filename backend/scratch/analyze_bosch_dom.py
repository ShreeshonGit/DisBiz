import json
from bs4 import BeautifulSoup

def main():
    # 1. Read DOM
    with open("scratch/bosch_debug/bosch_final_dom.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "lxml")
    
    # Let's search for dealer outlet list nodes
    # Looking at the initial DOM segment we saw: <div class="store-info-box">
    outlets = soup.select(".store-info-box")
    print(f"Number of dealer cards (.store-info-box): {len(outlets)}")
    
    # Print outer text of first few outlets
    for i, out in enumerate(outlets[:3]):
        name_node = out.select_one(".outlet-name")
        name = name_node.get_text().strip() if name_node else "No name node"
        address_node = out.select_one(".outlet-address")
        address = address_node.get_text().strip() if address_node else "No address node"
        print(f"  Outlet {i+1}: {name} -- {address}")
        
    # 2. Inspect intercepted requests
    with open("scratch/bosch_debug/intercepted_requests.json", "r", encoding="utf-8") as f:
        reqs = json.load(f)
        
    print(f"\nTotal intercepted requests: {len(reqs)}")
    
    # Print requests that contain "outlet", "store", "dealer", "search"
    keywords = ["outlet", "store", "dealer", "search", "autocomplete", "iq"]
    matching_reqs = []
    for r in reqs:
        url_lower = r["url"].lower()
        if any(kw in url_lower for kw in keywords):
            matching_reqs.append(r)
            
    print(f"\nMatching requests ({len(matching_reqs)}):")
    for r in matching_reqs[:15]:
        print(f"  {r['method']} {r['url'][:80]} - Status: {r['status']} - Size: {r['response_size']}")
        # Check if json
        if "application/json" in r["content_type"] or r["body_truncated"].strip().startswith(("{", "[")):
            try:
                body = json.loads(r["body_truncated"])
                print(f"    JSON keys: {list(body.keys())}")
            except Exception:
                # Might be truncated
                print(f"    Body start: {r['body_truncated'][:150]}")
        else:
            print(f"    Body snippet: {r['body_truncated'][:150].replace('\n', ' ')}")

if __name__ == "__main__":
    main()
