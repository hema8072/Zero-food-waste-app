import sqlite3

conn = sqlite3.connect("users.db")

conn.execute(
    """
    UPDATE food_requests
    SET status='Pending'
    WHERE status='Requested'
    """
)

conn.commit()

conn.close()

print("Status updated")