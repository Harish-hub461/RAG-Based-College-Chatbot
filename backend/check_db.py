import sys
sys.path.insert(0, ".")

try:
    from app.core.database import engine
    from sqlalchemy import text

    conn = engine.connect()
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [r[0] for r in result]
    conn.close()

    print("DATABASE CONNECTED OK!")
    print("Tables found:", tables)

    conn2 = engine.connect()
    for table in tables:
        count = conn2.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  {table}: {count} rows")
    conn2.close()

except Exception as e:
    print(f"DATABASE ERROR: {e}")
