import sqlite3

def get_db():
    conn = sqlite3.connect(
        "planner.db",
        timeout=30,              # wait instead of failing
        check_same_thread=False
    )
    conn.execute("PRAGMA journal_mode=WAL;")  # allow concurrent reads/writes
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            subject TEXT,
            topic TEXT,
            hours REAL,
            completed INTEGER
        )
    """)
    return conn
