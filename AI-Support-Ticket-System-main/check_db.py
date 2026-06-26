import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "support_tickets.db"
)

df = pd.read_sql_query(
    "SELECT * FROM tickets",
    conn
)

print(df)

conn.close()