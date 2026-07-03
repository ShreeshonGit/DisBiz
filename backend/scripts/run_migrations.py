import os
import sys
import glob
import time
import argparse
from urllib.parse import urlparse
import psycopg2
from dotenv import load_dotenv

# Initialize colorama for Windows terminal ANSI color support
try:
    import colorama
    colorama.init()
except ImportError:
    pass

# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Find the absolute path to .env relative to scripts directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def main() -> None:
    """
    Main database migration command line interface.
    Supports standard execution and --dry-run mode.
    """
    parser = argparse.ArgumentParser(description="Dealer Discovery Platform - Migration Runner")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Simulate migrations and display status without making database modifications"
    )
    args = parser.parse_args()

    # 1. Verify DATABASE_URL exists
    if not DATABASE_URL:
        print(f"\n{RED}{BOLD}[ERROR] DATABASE_URL environment variable is missing from backend/.env{RESET}")
        print("Please configure your PostgreSQL database connection string in your .env file.")
        print("Format: DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres\n")
        sys.exit(1)

    # Parse host and database details for logging
    try:
        parsed_url = urlparse(DATABASE_URL)
        db_host = parsed_url.hostname or "unknown-host"
        db_name = parsed_url.path.lstrip('/') if parsed_url.path else "unknown-db"
    except Exception:
        db_host = "invalid-host"
        db_name = "invalid-db"

    print("---------------------------------------------------------")
    print(f"{BOLD}DEALER DISCOVERY PLATFORM - DATABASE MIGRATION ENGINE{RESET}")
    print("---------------------------------------------------------")
    print(f"Target Database: {CYAN}{db_name}{RESET} on Host: {CYAN}{db_host}{RESET}")
    print("Verifying connection...")

    # 2. Verify Database connection succeeds
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False  # Enforce explicit transaction control
        cursor = conn.cursor()
        print(f"{GREEN}Connection successful!{RESET}\n")
    except Exception as e:
        print(f"{RED}{BOLD}[CONNECTION ERROR] Database connection failed: {e}{RESET}\n")
        sys.exit(1)

    try:
        # 3. Ensure schema_migrations table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.commit()

        # Retrieve already executed migrations
        cursor.execute("SELECT version FROM schema_migrations;")
        executed_versions = {row[0] for row in cursor.fetchall()}

        # 4. Locate SQL files inside backend/migrations/ (Ignoring non-SQL files)
        migrations_dir = os.path.join(backend_dir, "migrations")
        if not os.path.exists(migrations_dir):
            print(f"{RED}[ERROR] Migrations directory '{migrations_dir}' does not exist.{RESET}")
            cursor.close()
            conn.close()
            sys.exit(1)

        # Glob and filter out non-SQL files, then sort alphabetically
        sql_files = glob.glob(os.path.join(migrations_dir, "*.sql"))
        sql_files.sort()

        if not sql_files:
            print(f"{YELLOW}[INFO] No migration SQL scripts (.sql) discovered.{RESET}")
            cursor.close()
            conn.close()
            return

        # 5. Handle DRY-RUN mode
        if args.dry_run:
            print(f"{YELLOW}{BOLD}--- DRY RUN MODE: Listing migrations without executing ---{RESET}\n")
            for file_path in sql_files:
                filename = os.path.basename(file_path)
                if filename in executed_versions:
                    print(f"  {YELLOW}✓ Applied: {filename}{RESET}")
                else:
                    print(f"  {GREEN}+ Pending: {filename}{RESET}")
            print("\n---------------------------------------------------------")
            print("Dry run completed. No changes were written to the database.")
            print("---------------------------------------------------------")
            cursor.close()
            conn.close()
            return

        # 6. Execute pending migrations
        start_time = time.time()
        applied_list = []
        skipped_list = []

        print("Executing pending migrations...\n")

        for file_path in sql_files:
            filename = os.path.basename(file_path)

            if filename in executed_versions:
                print(f"  {YELLOW}[SKIP]{RESET}  {filename} (Already applied)")
                skipped_list.append(filename)
                continue

            print(f"  [RUN]   {filename} ... ", end="", flush=True)
            
            try:
                # Read migration queries
                with open(file_path, "r", encoding="utf-8") as sql_file:
                    sql_query = sql_file.read()

                # Execute migration queries
                cursor.execute(sql_query)

                # Record in schema metadata
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s);",
                    (filename,)
                )

                # Commit changes for this migration
                conn.commit()
                print(f"{GREEN}SUCCESS{RESET}")
                applied_list.append(filename)

            except Exception as e:
                # Rollback changes to prevent half-applied migration states
                conn.rollback()
                print(f"{RED}FAILED{RESET}")
                print(f"\n{RED}{BOLD}[CRITICAL ERROR] Failed to run '{filename}': {e}{RESET}")
                print("Database transaction rolled back. Aborting subsequent migrations.\n")
                
                # Print summary showing failure
                print_summary(applied_list, skipped_list, time.time() - start_time)
                cursor.close()
                conn.close()
                sys.exit(1)  # Exit with code 1 on failure

        # Completed successfully
        print_summary(applied_list, skipped_list, time.time() - start_time)
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n{RED}[ERROR] Migration engine error: {e}{RESET}\n")
        sys.exit(1)

def print_summary(applied: list, skipped: list, duration: float) -> None:
    """Prints a structured summary of migration execution."""
    print("\n----------------------------------------")
    print(f"{BOLD}Migration Summary{RESET}")
    print("----------------------------------------")
    
    print("\nApplied:")
    if applied:
        for f in applied:
            print(f"  {GREEN}{f}{RESET}")
    else:
        print("  None")
        
    print("\nSkipped:")
    if skipped:
        for f in skipped:
            print(f"  {YELLOW}{f}{RESET}")
    else:
        print("  None")
        
    print(f"\nTotal Applied: {len(applied)}")
    print(f"Execution Time: {duration:.2f} seconds")
    print("----------------------------------------\n")

if __name__ == "__main__":
    main()
