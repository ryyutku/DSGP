# db.py
import sqlite3
from sqlite3 import Error
import bcrypt

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        return conn
    except Error as e:
        print(e)
    return conn

def initialize_database():
    """Initialize the database with required tables"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT,
                    fullname TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()



def add_user(username, password, email=None, fullname=None):
    """Add a new user to the database"""
    # Store hashed password as string to avoid SQLite byte storage issues
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, email, fullname) 
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_pw, email, fullname))
        conn.commit()
        return True
    except Error as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_user(username):
    """Get a user by username"""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def verify_user(username, password):
    """Verify user credentials"""
    user = get_user(username)
    if user:
        stored_password = user[2]  # password is at index 2
        # Convert back to bytes for bcrypt comparison
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    return False