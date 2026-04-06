import asyncio
import os
import sys
from sqlalchemy import text
from app.database import AsyncSessionLocal
from alembic.config import Config
from alembic import command

async def check_schema():
    print("Checking database schema consistency...")
    async with AsyncSessionLocal() as db:
        try:
            # Check if universities table has domain column
            result = await db.execute(text("PRAGMA table_info(universities)"))
            columns = [row[1] for row in result.fetchall()]
            if 'domain' in columns:
                print("⚠️  CRITICAL: 'domain' column still exists in 'universities' table!")
                return False
            print("✓ Database schema is consistent with ORM models.")
            return True
        except Exception as e:
            print(f"✗ Error checking schema: {e}")
            return False

async def run_migrations_async():
    print("Running database migrations...")
    # Since alembic env.py uses asyncio.run, we call it as a subprocess to avoid event loop conflicts
    import subprocess
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ Migrations failed: {result.stderr}")
        return False
    print("✓ Migrations completed.")
    return True

async def main():
    # 1. Run migrations
    if not await run_migrations_async():
        sys.exit(1)

    # 2. Check consistency
    if not await check_schema():
        sys.exit(1)

    # 3. Seed data
    print("Seeding demo data...")
    from scripts.seed import seed_data
    await seed_data()
    print("✓ Setup completed successfully!")

if __name__ == "__main__":
    # Ensure PYTHONPATH includes current directory
    sys.path.append(os.getcwd())
    asyncio.run(main())
