import sqlite3

conn = sqlite3.connect(
    "support_tickets.db"
)

cursor = conn.cursor()

try:

    cursor.execute(
        """
        ALTER TABLE tickets
        ADD COLUMN status TEXT
        """
    )

    print("Status Column Added Successfully!")

except:

    print("Status Column Already Exists!")

conn.commit()
conn.close()