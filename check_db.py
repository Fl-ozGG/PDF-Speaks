import sqlite3

conn = sqlite3.connect("iachatbot.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Query users table
cursor.execute("SELECT * FROM users;")
users = cursor.fetchall()
print("Users:", users)

conn.close()
