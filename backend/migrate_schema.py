import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "agentwatch.db"

if not DB_PATH.exists():
    raise SystemExit(f"Database not found at {DB_PATH}. Start the backend once to create it.")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

changes = {
    "projects": [
        ("retention_days", "INTEGER DEFAULT 90")
    ],
    "runs": [
        ("trace_id", "TEXT"),
        ("host", "TEXT"),
        ("pid", "INTEGER"),
        ("metadata", "TEXT")
    ],
    "spans": [
        ("parent_span_id", "INTEGER"),
        ("trace_id", "TEXT"),
        ("host", "TEXT"),
        ("pid", "INTEGER"),
        ("metadata", "TEXT")
    ],
    "evaluations": [
        ("metadata", "TEXT")
    ]
}

for table, cols in changes.items():
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    for column, col_def in cols:
        if column not in existing:
            print(f"Adding {column} to {table}")
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
        else:
            print(f"{table}.{column} already exists")

conn.commit()
conn.close()
print("Schema migration complete.")
