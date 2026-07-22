import sqlite3

conn = sqlite3.connect('users.db')

conn.execute(
    "ALTER TABLE food_donations ADD COLUMN status TEXT DEFAULT 'Available'"
)

conn.commit()

conn.close()

print("Status column added")