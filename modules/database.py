import sqlite3
import os
import json
from datetime import datetime

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'campusgpt.db')

def get_connection():
    """Establishes and returns a database connection with Row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database tables and seeds the admin user if needed."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        file_path TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        page_count INTEGER NOT NULL,
        file_size INTEGER NOT NULL,
        chunk_count INTEGER NOT NULL,
        uploaded_by INTEGER,
        FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # Create Chat History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        sources TEXT NOT NULL, -- JSON string representation
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Create Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating TEXT NOT NULL, -- 'helpful' or 'not_helpful'
        comments TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chat_history(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Create Searches table (semantic searches)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()

    # Seed Admin Account if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    if cursor.fetchone()[0] == 0:
        # Import inside here to prevent circular imports if helper is in auth.py
        import bcrypt
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, '.env'))

        admin_email = os.getenv('ADMIN_EMAIL', 'admin@campusgpt.edu')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin_name = os.getenv('ADMIN_NAME', 'CampusGPT Admin')

        # Hash default admin password
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                (admin_name, admin_email, pw_hash)
            )
            conn.commit()
            print(f"Database initialized. Seeded default admin account: {admin_email}")
        except sqlite3.IntegrityError:
            pass # Admin already exists with that email

    conn.close()

# --- User Management Operations ---

def add_user(name, email, password_hash, role='user'):
    """Adds a new user to the system."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Retrieves user info by email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Retrieves user info by user ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def list_users():
    """Lists all users in the system."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, created_at FROM users ORDER BY id ASC")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    """Deletes a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- Document Operations ---

def add_document(name, file_path, page_count, file_size, chunk_count, uploaded_by):
    """Adds an uploaded document and metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO documents (name, file_path, page_count, file_size, chunk_count, uploaded_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, file_path, page_count, file_size, chunk_count, uploaded_by)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_document_by_name(name):
    """Gets document details by filename."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE name = ?", (name,))
    doc = cursor.fetchone()
    conn.close()
    return doc

def list_documents():
    """Lists all uploaded documents."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.name, d.file_path, d.upload_date, d.page_count, d.file_size, d.chunk_count, u.name as uploaded_by_name 
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        ORDER BY d.upload_date DESC
    """)
    docs = cursor.fetchall()
    conn.close()
    return docs

def delete_document(doc_id):
    """Deletes a document from database and returns details for file deletion."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, file_path FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    if doc:
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
    conn.close()
    return doc

# --- Chat History & Feedback ---

def add_chat_entry(user_id, question, answer, sources):
    """Saves a conversation turn to SQLite database. sources should be a list/JSON."""
    conn = get_connection()
    cursor = conn.cursor()
    sources_json = json.dumps(sources)
    cursor.execute(
        "INSERT INTO chat_history (user_id, question, answer, sources) VALUES (?, ?, ?, ?)",
        (user_id, question, answer, sources_json)
    )
    conn.commit()
    chat_id = cursor.lastrowid
    conn.close()
    return chat_id

def get_chat_history(user_id, limit=50):
    """Loads chat history for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, question, answer, sources, timestamp 
           FROM chat_history 
           WHERE user_id = ? 
           ORDER BY timestamp ASC 
           LIMIT ?""",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            "id": r["id"],
            "question": r["question"],
            "answer": r["answer"],
            "sources": json.loads(r["sources"]),
            "timestamp": r["timestamp"]
        })
    return history

def clear_chat_history(user_id):
    """Deletes chat history for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_feedback(chat_id, user_id, rating, comments=None):
    """Saves user feedback on a response (👍 or 👎)."""
    conn = get_connection()
    cursor = conn.cursor()
    # Upsert feedback for this chat entry
    cursor.execute("SELECT id FROM feedback WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE feedback SET rating = ?, comments = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
            (rating, comments, existing["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO feedback (chat_id, user_id, rating, comments) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, rating, comments)
        )
    conn.commit()
    conn.close()

# --- Semantic Search Logging ---

def add_search(user_id, query):
    """Logs a semantic search query for analytics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO searches (user_id, query) VALUES (?, ?)", (user_id, query))
    conn.commit()
    conn.close()

# --- KPIs & Analytics Queries ---

def get_kpis():
    """Computes high-level KPIs for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(page_count) FROM documents")
    total_pages = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(chunk_count) FROM documents")
    total_chunks = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    conn.close()

    return {
        "total_docs": total_docs,
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "total_questions": total_questions,
        "total_users": total_users
    }

def get_analytics_metrics():
    """Retrieves deep analytics queries for graphing."""
    conn = get_connection()
    cursor = conn.cursor()

    # Storage space: file_size by document name
    cursor.execute("SELECT name, file_size FROM documents")
    docs_storage = [dict(row) for row in cursor.fetchall()]

    # Questions asked over time (grouped by date)
    cursor.execute("""
        SELECT DATE(timestamp) as date_val, COUNT(*) as count_val 
        FROM chat_history 
        GROUP BY date_val 
        ORDER BY date_val ASC
    """)
    questions_by_day = [dict(row) for row in cursor.fetchall()]

    # Searches over time (grouped by date)
    cursor.execute("""
        SELECT DATE(timestamp) as date_val, COUNT(*) as count_val 
        FROM searches 
        GROUP BY date_val 
        ORDER BY date_val ASC
    """)
    searches_by_day = [dict(row) for row in cursor.fetchall()]

    # User activity (number of questions by user)
    cursor.execute("""
        SELECT u.name, COUNT(ch.id) as count_val
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        GROUP BY u.name
        ORDER BY count_val DESC
        LIMIT 10
    """)
    user_activity = [dict(row) for row in cursor.fetchall()]

    # Feedback score breakdown
    cursor.execute("""
        SELECT rating, COUNT(*) as count_val 
        FROM feedback 
        GROUP BY rating
    """)
    feedback_scores = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "docs_storage": docs_storage,
        "questions_by_day": questions_by_day,
        "searches_by_day": searches_by_day,
        "user_activity": user_activity,
        "feedback_scores": feedback_scores
    }
