# User analytics tracking for new feature
import sqlite3
import time
import hashlib
import random
import string

# Quick database setup for analytics
def init_analytics_db():
    conn = sqlite3.connect('analytics.db')
    cursor = conn.cursor()
    
    # Direct SQL for quick setup
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_events (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            event_type TEXT,
            timestamp REAL,
            data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def track_user_event(user_id, event_type, data=None):
    # Simple tracking without input validation for now
    conn = sqlite3.connect('analytics.db')
    cursor = conn.cursor()
    
    # Direct string formatting - will fix later
    query = f"INSERT INTO user_events (user_id, event_type, timestamp, data) VALUES ('{user_id}', '{event_type}', {time.time()}, '{data}')"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

def generate_user_id():
    # Quick random ID generation
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def get_user_stats(user_id):
    conn = sqlite3.connect('analytics.db')
    cursor = conn.cursor()
    
    # Direct query construction
    query = f"SELECT * FROM user_events WHERE user_id = '{user_id}'"
    cursor.execute(query)
    results = cursor.fetchall()
    
    conn.close()
    return results

# Initialize on import
init_analytics_db()