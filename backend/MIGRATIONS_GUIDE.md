# Database Migrations Guide - Dealer Discovery Platform

This guide explains how to manage, configure, and execute database schema migrations for the **Dealer Discovery Platform** backend.

---

## 1. Migration Setup

All migration files are stored as plain SQL scripts in:
`backend/migrations/`

They are named chronologically and executed in alphanumeric order:
- `001_init_brands.sql`
- `002_add_scraper_tables.sql`
- `003_add_indexes.sql`

Only files ending with `.sql` are processed; any other metadata or configuration files placed in the directory are ignored automatically.

---

## 2. Local Environment Configuration

The migrations runner connects directly to your PostgreSQL instance using `psycopg2` and requires a connection URI configured in your `backend/.env` file.

1. Open your local `backend/.env` file.
2. Locate or add the `DATABASE_URL` parameter.
3. Construct the database URI with your database password (you can locate your project reference ID in your Supabase project settings):
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres
   ```
   *Note: Replace `[YOUR-PASSWORD]` with your actual database password, and `[YOUR-PROJECT-ID]` with your Supabase project reference.*

---

## 3. Running Migrations Locally

First, open a terminal and navigate to the backend folder and activate your virtual environment:
```bash
cd dealer-discovery-platform/backend
# On Windows (PowerShell)
..\venv\Scripts\Activate.ps1
# On Linux/macOS
source ../venv/bin/activate
```

### A. Dry Run Mode (Preview Pending Migrations)
You can preview which migrations have already been applied and which are pending execution without writing any DDL or changing the database schema:

```bash
python scripts/run_migrations.py --dry-run
```

#### Expected CLI Output:
```text
---------------------------------------------------------
DEALER DISCOVERY PLATFORM - DATABASE MIGRATION ENGINE
---------------------------------------------------------
Target Database: postgres on Host: db.orzvschsdkbptfvqehoq.supabase.co
Verifying connection...
Connection successful!

--- DRY RUN MODE: Listing migrations without executing ---

  ✓ Applied: 001_init_brands.sql
  + Pending: 002_add_scraper_tables.sql
  + Pending: 003_add_indexes.sql

---------------------------------------------------------
Dry run completed. No changes were written to the database.
---------------------------------------------------------
```

### B. Standard Run Mode (Apply Pending Migrations)
To execute pending SQL migrations and record them in the database:

```bash
python scripts/run_migrations.py
```

#### Expected CLI Output:
```text
---------------------------------------------------------
DEALER DISCOVERY PLATFORM - DATABASE MIGRATION ENGINE
---------------------------------------------------------
Target Database: postgres on Host: db.orzvschsdkbptfvqehoq.supabase.co
Verifying connection...
Connection successful!

Executing pending migrations...

  [SKIP]  001_init_brands.sql (Already applied)
  [RUN]   002_add_scraper_tables.sql ... SUCCESS
  [RUN]   003_add_indexes.sql ... SUCCESS

----------------------------------------
Migration Summary
----------------------------------------

Applied:
  002_add_scraper_tables.sql
  003_add_indexes.sql

Skipped:
  001_init_brands.sql

Total Applied: 2
Execution Time: 0.18 seconds
----------------------------------------
```

*Note: The script outputs colorized logs (Green for SUCCESS/Pending, Yellow for SKIPPED/Applied, and Red for FAILED).*

---

## 4. Running Migrations in Production

When deploying to production, follow these steps:

### A. Environment Configuration
Ensure your deployment server has the production environment variable configured:
```bash
DATABASE_URL=postgresql://postgres:[PROD-PASSWORD]@db.[PROD-PROJECT-ID].supabase.co:5432/postgres
```
*Never hardcode production passwords or commit `.env` files to git.*

### B. Deployment Pipeline Integration
Integrate the migration runner as a post-deploy step in your CI/CD pipeline (e.g., GitHub Actions, AWS CodeBuild, Heroku release phase).

Example pipeline step:
```yaml
- name: Run Database Migrations
  env:
    DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
  run: |
    cd backend
    python -m pip install -r requirements.txt
    python scripts/run_migrations.py
```

### C. Manual Production Migrations
If you need to run migrations manually against production:
1. Ensure your IP address is whitelisted in your Supabase Database Network / Security settings.
2. Set the production connection URI in your shell and execute:
   - Windows PowerShell:
     ```powershell
     $env:DATABASE_URL="postgresql://postgres:[PROD-PASSWORD]@db.[PROD-PROJECT-ID].supabase.co:5432/postgres"
     python scripts/run_migrations.py
     ```
   - Linux/macOS Bash:
     ```bash
     DATABASE_URL="postgresql://postgres:[PROD-PASSWORD]@db.[PROD-PROJECT-ID].supabase.co:5432/postgres" python scripts/run_migrations.py
     ```
