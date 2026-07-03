import sys
import time
import os
from uuid import UUID
from fastapi.testclient import TestClient

sys.path.insert(0, ".")
from main import app

# Ensure env variables are loaded
from dotenv import load_dotenv
load_dotenv()

def run_integration_test():
    client = TestClient(app)
    brand_id = "aec01b75-0c61-47fa-bd34-a09b0d7664d9" # Lava Brand ID

    print("---------------------------------------------------------")
    print("DEALER DISCOVERY PLATFORM - FULL SCRAPE INTEGRATION TEST")
    print("---------------------------------------------------------")

    # Step 1: Trigger Auto-Detection
    print("\n[STEP 1] Running auto-detection...")
    detect_res = client.post("/api/v1/scraper/detect", json={"brand_id": brand_id})
    print(f"Status Code: {detect_res.status_code}")
    detect_data = detect_res.json()
    print(f"Response: {detect_data}")
    if detect_res.status_code != 200 or not detect_data.get("success"):
        print("[ERROR] Auto-detection failed.")
        sys.exit(1)

    # Step 2: Trigger Full Scrape Job
    print("\n[STEP 2] Starting full scrape job...")
    start_res = client.post(f"/api/v1/scraper/start/{brand_id}")
    print(f"Status Code: {start_res.status_code}")
    start_data = start_res.json()
    print(f"Response: {start_data}")
    if start_res.status_code != 200 or not start_data.get("success"):
        print("[ERROR] Failed to start scrape job.")
        sys.exit(1)

    job_id = start_data["data"]["id"]
    print(f"Queued Scrape Job ID: {job_id}")

    # Step 3: Poll Job Status until Completed, Failed or Cancelled
    print("\n[STEP 3] Polling job status...")
    max_polls = 10
    poll_count = 0
    job_completed = False
    
    while poll_count < max_polls:
        poll_count += 1
        time.sleep(2)
        
        job_res = client.get(f"/api/v1/scraper/jobs/{job_id}")
        if job_res.status_code != 200:
            print(f"[ERROR] Failed to poll job details: {job_res.text}")
            sys.exit(1)
            
        job_data = job_res.json()["data"]
        status = job_data["status"]
        print(f"Poll {poll_count}/{max_polls}: Status = {status}, Records Saved = {job_data['records_saved']}")
        
        if status in ["Completed", "Failed", "Cancelled"]:
            job_completed = True
            break

    if not job_completed:
        print("[ERROR] Job timed out without completing.")
        sys.exit(1)

    # Fetch final details
    final_job_res = client.get(f"/api/v1/scraper/jobs/{job_id}")
    final_job = final_job_res.json()["data"]
    print("\nFinal Job State:")
    print(f"  Status: {final_job['status']}")
    print(f"  Records Scraped: {final_job.get('records_scraped')}")
    print(f"  Records Saved: {final_job.get('records_saved')}")
    print(f"  Execution Time: {final_job.get('duration_seconds')} seconds")
    print(f"  Error Message: {final_job.get('error_message')}")
    
    print("\nExecution Logs:")
    for log_line in final_job.get("execution_logs", []):
        print(f"  {log_line}")

    if final_job["status"] != "Completed":
        print(f"\n[ERROR] Job failed with status: {final_job['status']}")
        sys.exit(1)

    # Step 4: Verify Dealers exist in DB
    print("\n[STEP 4] Verifying dealers in database...")
    import psycopg2
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT id, dealer_name, city, pincode FROM dealers WHERE brand_id = %s;", (brand_id,))
    dealers = cur.fetchall()
    print(f"Found {len(dealers)} dealers in database for brand ID {brand_id}:")
    for d in dealers:
        print(f"  - Name: {d[1]}, City: {d[2]}, Pincode: {d[3]} (ID: {d[0]})")
    
    conn.close()
    
    if len(dealers) == 0:
        print("[ERROR] No dealers found in database!")
        sys.exit(1)

    print("\n---------------------------------------------------------")
    print("INTEGRATION TEST SUCCESSFUL! ALL FLOWS VERIFIED.")
    print("---------------------------------------------------------")

if __name__ == "__main__":
    run_integration_test()
