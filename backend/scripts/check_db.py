import asyncio
from sqlalchemy import create_engine, inspect
from app.database import DATABASE_URL

def check_db():
    # sync engine for inspection
    sync_url = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
    engine = create_engine(sync_url)
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    print(f"Tables: {tables}")

    for table in tables:
        columns = inspector.get_columns(table)
        print(f"Table {table} columns: {[c['name'] for c in columns]}")

if __name__ == "__main__":
    check_db()
