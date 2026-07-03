# Dealer Discovery Platform - Sprint 3.5 Stable

A production-grade, highly resilient data extraction engine and search locator portal designed to scrape, clean, deduplicate, validate, and search authorized retail outlets and service centers.

---

## 🏗️ System Architecture

```mermaid
graph TD
    PublicPortal[Next.js Public Portal<br>Port 3000] -->|Search API| FastAPI[FastAPI Backend<br>Port 8000]
    AdminPortal[Next.js Admin Console<br>Port 3001] -->|Scraper Controls| FastAPI
    FastAPI -->|PostgREST Async| Supabase[(Supabase PostgreSQL)]
    FastAPI -->|Background Tasks| ScraperRunner[Scraper Job Runner]
    ScraperRunner -->|Strategy Selector| ScrapingEngine[API / Static / Playwright]
```

### Key Subsystems:
1. **Production Scraper Engine**: Real-time strategy detection (Hidden API ➔ Static HTML ➔ Playwright), selector fallback heuristics, and recovery manager (up to 3 retries, checkpoint saving).
2. **Deduplication & Validation**: Normalizes geographic coordinates, cleans emails/phone values, and runs Jaccard overlap string deduplication.
3. **Database Repository Layer**: Enforces relational data-integrity, connection pools, and logs real-time scraper metrics.
4. **Admin Dashboard**: Real-time log streaming, job control parameters, strategy distribution, and CSV export capabilities.
5. **Public Search Portal**: Fully responsive locator interface featuring dynamic keyword matching, state/city filters, quality-based sorting, and integrated Google Maps hooks.

---

## 🛠️ Environment Configuration

### Backend Setup:
1. **Create Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. **Configure `.env`**:
   Create a `.env` in the `backend/` directory:
   ```env
   PROJECT_NAME="Dealer Discovery Platform"
   API_V1_STR="/api/v1"
   SUPABASE_URL="https://your-project.supabase.co"
   SUPABASE_ANON_KEY="your-anon-key"
   SUPABASE_SERVICE_KEY="your-service-role-key"
   DATABASE_URL="postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres"
   ```

3. **Run Schema Migrations**:
   Execute our zero-dependency Python migration tool:
   ```bash
   python scripts/run_migrations.py
   ```

4. **Start Backend Server**:
   ```bash
   python main.py
   ```
   The backend API will boot up on `http://localhost:8000`.

---

## 💻 Frontend Configuration

### Admin Frontend (Next.js):
```bash
cd frontend-admin
npm install
npm run dev
```
Accessible on `http://localhost:3001`.

### Public Search Frontend (Next.js):
```bash
cd frontend-public
npm install
npm run dev
```
Accessible on `http://localhost:3000`.

---

## 🧪 Testing Suite

We maintain a 100% passing test coverage suite verifying core parsers, fallback engines, API routers, and deduplicators:

```bash
cd backend
python -m pytest -v
```

---

## 🧼 Standardized API Error Schemes

All API endpoints intercept request parsing exceptions and raise a uniform production response shape, preventing database stack traces from leaking to the frontend client:

```json
{
    "success": false,
    "message": "Error details here...",
    "error_code": "VALIDATION_ERROR | INTERNAL_SERVER_ERROR | HTTP_404_ERROR",
    "details": {
        "errors": ["Specific field validation failures..."]
    }
}
```

---

## 🔧 Troubleshooting Guide

### Lava Mobiles SSL Expiry:
- The Lava Mobiles domain certificate occasionally expires. Our scraper engine overrides certificate validation in Python by passing `verify=False` to httpx clients to prevent connection blocks.

### Playwright Headless Configuration:
- If Playwright fails to initialize in Docker/VM environments, run the browser installer tool:
  ```bash
  playwright install chromium
  ```
