import sqlite3

# Connect (or create) a database file called users.db
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create table for users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ users.db created with 'users' table")
