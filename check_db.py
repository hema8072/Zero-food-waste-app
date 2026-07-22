import sqlite3

conn = sqlite3.connect("users.db")

conn.row_factory = sqlite3.Row


print("\nREGISTERED USERS:")
users = conn.execute(
    "SELECT * FROM users"
).fetchall()

for user in users:
    print(dict(user))


print("\nFOOD DONATIONS:")
foods = conn.execute(
    "SELECT * FROM food_donations"
).fetchall()

for food in foods:
    print(dict(food))


print("\nFOOD REQUESTS:")
requests = conn.execute(
    "SELECT * FROM food_requests"
).fetchall()

for r in requests:
    print(dict(r))


print("\nADMINS:")
admins = conn.execute(
    "SELECT * FROM admin"
).fetchall()

for a in admins:
    print(dict(a))


conn.close()