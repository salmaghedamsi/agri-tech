import sqlite3
import os

# Path to the database
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'agriconnect.db')

if not os.path.exists(DB_PATH):
    print(f"Database file not found at {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def get_columns(table):
    cur.execute(f"PRAGMA table_info('{table}')")
    rows = cur.fetchall()
    return [r[1] for r in rows]

try:
    for table in ('courses', 'course_modules'):
        cols = get_columns(table)
        print(f"{table} columns before: {cols}")
        if 'document_path' not in cols:
            print(f"Adding document_path column to {table}...")
            cur.execute(f"ALTER TABLE {table} ADD COLUMN document_path TEXT")
            conn.commit()
            cols_after = get_columns(table)
            print(f"{table} columns after: {cols_after}")
        else:
            print(f"{table} already has document_path column; skipping")

    print("Done. If your app was running, retry the failing endpoints.")
except Exception as e:
    print('Error while modifying database:', e)
    raise
finally:
    cur.close()
    conn.close()
