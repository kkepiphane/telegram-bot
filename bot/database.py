import sqlite3
from datetime import datetime
from config import Config

def init_db():
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            language TEXT,
            category TEXT,
            votes INTEGER DEFAULT 0,
            date_added TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            reported_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            group_id INTEGER,
            reporter_id INTEGER,
            reason TEXT,
            date_reported TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(Config.DB_NAME)