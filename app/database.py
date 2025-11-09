import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = os.environ.get('DB_PATH', 'wishlist.db')
            # If the DB is in the parent directory (where the bot is)
            if not os.path.exists(db_name) and os.path.exists(os.path.join('..', db_name)):
                db_name = os.path.join('..', db_name)
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Creates a new database connection."""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initializes the database schema."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users
                         (user_id INTEGER PRIMARY KEY,
                          username TEXT,
                          first_name TEXT,
                          created_at TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS wishlists
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          name TEXT,
                          is_free INTEGER DEFAULT 1,
                          created_at TIMESTAMP,
                          FOREIGN KEY (user_id) REFERENCES users(user_id))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS items
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          wishlist_id INTEGER,
                          title TEXT,
                          description TEXT,
                          url TEXT,
                          image_url TEXT,
                          is_free INTEGER DEFAULT 1,
                          created_at TIMESTAMP,
                          FOREIGN KEY (wishlist_id) REFERENCES wishlists(id))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS settings
                         (key TEXT PRIMARY KEY,
                          value TEXT,
                          updated_at TIMESTAMP)''')
            conn.commit()

    def execute(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        """A generic method to execute queries."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(query, params)
            
            if commit:
                conn.commit()
                return c.lastrowid

            if fetchone:
                return c.fetchone()
            
            if fetchall:
                return c.fetchall()

# Instantiate a single DB object for the application
db = Database()

def get_setting(key, default_value):
    """Gets a setting from the DB."""
    result = db.execute('SELECT value FROM settings WHERE key = ?', (key,), fetchone=True)
    if result:
        try:
            # Try to convert to int, otherwise return as is
            return int(result[0])
        except (ValueError, TypeError):
            return result[0]
    return default_value

def update_setting(key, value):
    """Updates a setting in the DB."""
    db.execute('''INSERT OR REPLACE INTO settings (key, value, updated_at)
                  VALUES (?, ?, ?)''',
               (key, str(value), datetime.now()), commit=True)

def init_default_settings(settings_dict):
    """Initializes default settings if they don't exist."""
    with db.get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM settings')
        if c.fetchone()[0] == 0:
            logger.info("Initializing default settings in the database.")
            for key, value in settings_dict.items():
                c.execute('''INSERT INTO settings (key, value, updated_at)
                             VALUES (?, ?, ?)''',
                         (key, str(value), datetime.now()))
            conn.commit()
        else:
            logger.info("Settings already initialized.")

