# Dealer Discovery Platform

A production-grade, highly resilient data extraction engine and dealer locator portal designed to scrape, clean, deduplicate, validate, and search authorized retail outlets and service centers across India.

---

## 🚀 Project Highlights
- **Universal Autonomous Scraper**: Automatically identifies site strategies (Hidden JSON API ➔ Static HTML ➔ Playwright rendering) without brand-specific code or hardcoded selectors. Handles cookie consent banner bypasses, infinite scroll, and coordinates mapping.
- **Data Quality & Deduplication**: Employs Jaccard overlap algorithms, contact details scrubbing (emails, phones), and verification status flags to maintain data integrity.
- **Redesigned Public Portal**: Premium customer-facing search dashboard built on **Next.js 15 + React 19 + Tailwind CSS + Framer Motion**, featuring category megamenu dropdowns, mobile drawer filters, dynamic brand counts, and coordinates maps.
- **Admin Dashboard Console**: Real-time log streaming, job parameters configuration, telemetry monitoring, and data exports.

---

## 🏗️ System Architecture Overview

```mermaid
graph TD
    PublicPortal[Next.js Public Portal<br>Port 3000] -->|Search API| FastAPI[FastAPI Backend<br>Port 8000]
    AdminPortal[Next.js Admin Console<br>Port 3001] -->|Scraper Controls| FastAPI
    FastAPI -->|PostgREST Client| Supabase[(Supabase PostgreSQL)]
    FastAPI -->|Background Tasks| ScraperRunner[Scraper Job Runner]
    ScraperRunner -->|Strategy Selector| ScrapingEngine[API / Static / Playwright]
```

For a deep-dive into codebases, layouts, and data quality algorithms, please check [ARCHITECTURE.md](file:///D:/DisBiz/dealer-discovery-platform/ARCHITECTURE.md).

---

## 🛠️ Environment Configuration

### 1. Backend Setup (FastAPI)
1. **Navigate and Create Environment**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Settings (`.env`)**:
   Create a `.env` in `backend/` containing:
   ```env
   PROJECT_NAME="Dealer Discovery Platform"
   API_V1_STR="/api/v1"
   SUPABASE_URL="https://your-project.supabase.co"
   SUPABASE_ANON_KEY="your-anon-key"
   SUPABASE_SERVICE_KEY="your-service-role-key"
   DATABASE_URL="postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres"
   ```
4. **Execute Database Migrations**:
   ```bash
   python scripts/run_migrations.py
   ```
5. **Start FastAPI Backend Server**:
   ```bash
   python main.py
   ```
   API runs at `http://localhost:8000`. Documentation available at `http://localhost:8000/docs`.

### 2. Admin Console Setup (Next.js)
1. **Navigate and Install**:
   ```bash
   cd frontend-admin
   npm install
   ```
2. **Run Dev Environment**:
   ```bash
   npm run dev
   ```
   Runs at `http://localhost:3001`.

### 3. Public Portal Setup (Next.js 15)
1. **Navigate and Install**:
   ```bash
   cd frontend-public
   npm install
   ```
2. **Run Dev Environment**:
   ```bash
   npm run dev
   ```
   Runs at `http://localhost:3000`.

---

## 🧪 Testing Suite
We maintain unit and integration tests verifying parsers, scrapers, deduplication algorithms, and endpoints.
To execute tests:
```bash
cd backend
python -m pytest -v
```

---

## 📁 Repository Directory Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI routers (brands, dealers, scrapers)
│   │   ├── database/        # Supabase and PostgreSQL connections
│   │   ├── models/          # DB schemas (pydantic & ORM structures)
│   │   ├── repositories/    # Database Repository layers
│   │   ├── scrapers/        # GenericScraper & strategy detection subclasses
│   │   └── services/        # Business logic (job runners, deduplication, loggers)
│   ├── scripts/             # Migration and testing utility scripts
│   └── main.py              # Application entrypoint
├── frontend-admin/          # Next.js Admin portal (Scraping logs & status)
├── frontend-public/         # Next.js 15 Public Customer portal
│   ├── src/
│   │   ├── app/             # App Router layout and main pages
│   │   ├── components/      # Reusable visual components (Navbar, Stats, Cards)
│   │   └── lib/             # API clients and styles helpers
└── README.md                # Project startup index (This file)
```
