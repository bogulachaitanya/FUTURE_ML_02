import sqlite3

conn = sqlite3.connect(
    "support_tickets.db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE tickets(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ticket_id TEXT,

    category TEXT,

    priority TEXT,

    confidence REAL,

    timestamp TEXT

)
""")

conn.commit()

conn.close()

print("Database Created Successfully!")
