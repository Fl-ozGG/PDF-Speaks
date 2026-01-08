import sqlite3
import auth

DB_FILE = "iachatbot.db"

def get_db_connection():
    """Return a connection to the SQLite DB."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Create the users table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_user(username: str, password: str) -> bool:
    """Insert a new user with hashed password. Returns False if user exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    hashed_pw = auth.get_password_hash(password)
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, hashed_pw))
    conn.commit()
    conn.close()
    return True

def get_user(username: str):
    """Return a user dict or None if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": row["name"], "hashed_password": row["password"]}
    return None
