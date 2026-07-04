import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

sys.path.insert(0, ".")

async def main():
    locator_url = "https://brandstores.bosch-home.in/"
    print(f"Starting Bosch locator debugging: {locator_url}")
    
    # Create screenshots and outputs folder if not exists
    os.makedirs("scratch/bosch_debug", exist_ok=True)
    
    intercepted_requests = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        async def handle_response(response):
            try:
                url = response.url
                status = response.status
                method = response.request.method
                headers = response.headers
                content_type = headers.get("content-type", "").lower()
                
                body_text = ""
                try:
                    body_text = await response.text()
                except Exception:
                    pass
                
                resp_size = len(body_text) if body_text else 0
                
                req_entry = {
                    "url": url,
                    "method": method,
                    "status": status,
                    "content_type": content_type,
                    "response_size": resp_size,
                    "body_truncated": body_text[:10240] if body_text else ""
                }
                intercepted_requests.append(req_entry)
                
                print(f"[NET] {method} {url[:80]} - Status: {status} ({content_type}) - Size: {resp_size}")
            except Exception as e:
                print(f"[NET ERROR] {e}")
                
        page.on("response", handle_response)
        
        # 1. Page Load
        print("[STEP] Loading Bosch page...")
        await page.goto(locator_url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        await page.screenshot(path="scratch/bosch_debug/page_loaded.png")
        print("[OK] Saved page_loaded.png")
        
        # 2. Check for search inputs
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='search' i]",
            "input[placeholder*='city' i]",
            "input[placeholder*='pincode' i]",
            "input[placeholder*='location' i]",
            "input[id*='search' i]",
            "input[id*='location' i]",
            "input[class*='search' i]",
            "input[class*='autocomplete' i]",
            "input.autocomplete",
            "input[name*='search' i]",
            "input[name*='city' i]",
            "input[name*='pincode' i]",
            "input[type='text']"
        ]
        
        search_input = None
        detected_selector = None
        for sel in search_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible() and await elem.is_enabled():
                    search_input = elem
                    detected_selector = sel
                    break
            except Exception:
                pass
                
        if not search_input:
            print("[ERROR] No search input field detected!")
            # Dump DOM to see why
            dom_content = await page.content()
            with open("scratch/bosch_debug/bosch_no_input_dom.html", "w", encoding="utf-8") as f:
                f.write(dom_content)
            await browser.close()
            return
            
        print(f"[OK] Detected search field: '{detected_selector}'")
        
        # 3. Enter keyword
        keyword = "Noida"
        print(f"[STEP] Typing keyword: {keyword}")
        await search_input.click()
        await search_input.fill("")
        await page.wait_for_timeout(500)
        await search_input.type(keyword, delay=150)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="scratch/bosch_debug/after_typing.png")
        print("[OK] Saved after_typing.png")
        
        # 4. Check for dropdown suggestions
        suggestion_selectors = [
            ".pac-container .pac-item",
            "[class*='suggestion' i]",
            "[class*='autocomplete' i] div",
            "[class*='dropdown' i] li",
            "[class*='result' i]",
            "ul[role='listbox'] li",
            "[id*='suggestion' i]",
            "[id*='results' i]",
            ".search-results div",
            "li.ui-menu-item",
            "[role='option']"
        ]
        
        suggestions = []
        sugg_texts = []
        for sugg_sel in suggestion_selectors:
            try:
                elems = await page.query_selector_all(sugg_sel)
                visible_elems = []
                for el in elems:
                    if await el.is_visible():
                        visible_elems.append(el)
                if visible_elems:
                    suggestions = visible_elems
                    sugg_texts = [await el.inner_text() for el in visible_elems]
                    break
            except Exception:
                pass
                
        await page.screenshot(path="scratch/bosch_debug/after_dropdown.png")
        print("[OK] Saved after_dropdown.png")
        
        if suggestions:
            print(f"[OK] Suggestions detected: {sugg_texts}")
            target_sugg = suggestions[0]
            print(f"[STEP] Selecting suggestion: {sugg_texts[0]}")
            await target_sugg.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="scratch/bosch_debug/after_selection.png")
            print("[OK] Saved after_selection.png")
        else:
            print("[WARN] No suggestions found. Submitting with Enter.")
            await search_input.press("Enter")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="scratch/bosch_debug/after_selection.png")
            print("[OK] Saved after_selection.png")
            
        # 5. Wait for results to load
        print("[STEP] Waiting for results / ajax calls to settle...")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="scratch/bosch_debug/after_results.png")
        print("[OK] Saved after_results.png")
        
        # 6. Dump DOM
        final_dom = await page.content()
        with open("scratch/bosch_debug/bosch_final_dom.html", "w", encoding="utf-8") as f:
            f.write(final_dom)
        print("[OK] Saved bosch_final_dom.html")
        
        # Write intercepted requests to file
        with open("scratch/bosch_debug/intercepted_requests.json", "w", encoding="utf-8") as f:
            json.dump(intercepted_requests, f, indent=2)
        print("[OK] Saved intercepted_requests.json")
        
        await browser.close()
        print("Debugging session complete.")

if __name__ == "__main__":
    asyncio.run(main())
