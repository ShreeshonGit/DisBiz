# Dealer Discovery Platform - Developer & Troubleshooting Guide

This guide walks you through common developer workflows, code contribution rules, schema migrations, and resolving environment-specific errors.

---

## 1. Local Environment Troubleshooting

### Playwright Issues
If Playwright is missing executable binaries, run the installer:
```bash
npx playwright install chromium
```
Ensure that Chromium executes in headless mode. Headless mode defaults to `True` in `GenericScraper`.

### SSL Domain Failures
If target websites have expired SSL certificates (e.g. Lava Mobile's backend APIs), our scraper passes `ignore_https_errors=True` inside browser context declarations:
```python
context = await browser.new_context(ignore_https_errors=True)
```
Do not remove this override as it is critical for scraping older or poorly configured regional servers.

---

## 2. Dynamic Selector Additions
To add new default CSS selector mappings for fallback HTML scraping, edit `discover_selectors()` inside [generic_scraper.py](file:///D:/DisBiz/dealer-discovery-platform/backend/app/scrapers/generic_scraper.py):

```python
# To add class name keywords:
name_classes = ["store-name", "dealer-title", "location-name"]
```
The scraper uses case-insensitive fuzzy matches to dynamically group attributes.

---

## 3. Database Schema Migrations
Database tables are managed via simple SQL files.
- To add a new migration, place a new `.sql` file inside `backend/app/database/migrations/`.
- Run the migration runner tool:
  ```bash
  python scripts/run_migrations.py
  ```
This ensures zero-dependency execution across both local and production databases.

---

## 4. Frontend Component Guidelines
To maintain code quality and layout alignment:
1. **Line Limit Constraint**: No React or Next.js component should exceed **300 lines of code**. Large functions must be refactored into helpers or split into nested elements.
2. **Tailwind Themes**: Use standard variables (`var(--background)`, `var(--foreground)`) or standard Tailwind classes rather than hardcoding colors.
3. **Accessibility**: All interactive elements must contain `aria-label` tags, focus selectors, and semantic wrapper elements.
