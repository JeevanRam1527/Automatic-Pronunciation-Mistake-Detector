import sqlite3
from sentence import init_sentences, get_random_sentence

def init_db():
    """
    Initializes the user database.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    """
    Adds a new user to the database.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False  # User already exists
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

def validate_user(username, password):
    """
    Validates the username and password.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def init_practice_history_db():
    """
    Initializes the practice history database.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS practice_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sentence TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_practice_result(user_id, sentence, score):
    """
    Saves a practice result to the database.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Get the actual user ID from the username
    c.execute("SELECT id FROM users WHERE username=?", (user_id,))
    user_row = c.fetchone()
    if user_row:
        db_user_id = user_row[0]
        c.execute("INSERT INTO practice_history (user_id, sentence, score) VALUES (?, ?, ?)",
                  (db_user_id, sentence, score))
        conn.commit()
    conn.close()

def get_practice_history(user_id, limit=None, offset=None):
    """
    Fetches the practice history for a given user, ordered by most recent first.
    Supports pagination using limit and offset.
    Returns a list of tuples: (sentence, score, timestamp)
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Get the actual user ID from the username
    c.execute("SELECT id FROM users WHERE username=?", (user_id,))
    user_row = c.fetchone()
    history = []
    if user_row:
        db_user_id = user_row[0]
        query = "SELECT sentence, score, timestamp FROM practice_history WHERE user_id=? ORDER BY timestamp DESC"
        params = [db_user_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        if offset is not None:
            query += " OFFSET ?"
            params.append(offset)
        c.execute(query, params)
        history = c.fetchall()
    conn.close()
    return history

# Import the sentence-related functions
# Initialize the practice history table on startup
init_practice_history_db()
def init_sentences_db():
    """
    Calls the function to initialize sentences in the database.
    """
    init_sentences()

def get_random_sentence_from_db(difficulty):
    """
    Fetches a random sentence from the database based on the difficulty.
    """
    return get_random_sentence(difficulty)
