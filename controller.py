import sqlite3
import os
import sys
from pathlib import Path

# Get base path for assets or data (works after build too)
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Executable mode
        return os.path.join(os.getenv("APPDATA"), "Wordspire_by_merajcode")
    else:
        # Script mode
        return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()
storage_folder = os.path.join(base_path, 'data')
db_path = os.path.join(storage_folder, "wallpaper.db")

DB_PATH = Path(db_path)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# Connect to DB
def get_connection():
    return sqlite3.connect(DB_PATH)

# Initialize DB with tables
def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT,
                example TEXT
            )
        ''')
        conn.commit()

# === Quotes ===
def add_quote(quote):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO quotes (quote) VALUES (?)", (quote,))
        conn.commit()

def update_quote(id, quote):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE quotes SET quote = ? WHERE id = ?", (quote, id))
        conn.commit()

def delete_quote(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quotes WHERE id = ?", (id,))
        conn.commit()

def get_all_quotes():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, quote FROM quotes")
            return cursor.fetchall()
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("⚠️ Table 'quotes' not found. Returning empty list.")
            return []
        else:
            raise  # Any other DB error should be raised

# === Vocabulary ===
def add_vocab(word, meaning, example):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vocab (word, meaning, example) VALUES (?, ?, ?)", (word, meaning, example))
        conn.commit()

def update_vocab(id, word, meaning, example):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE vocab SET word = ?, meaning = ?, example = ? WHERE id = ?", (word, meaning, example, id))
        conn.commit()

def delete_vocab(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vocab WHERE id = ?", (id,))
        conn.commit()

def get_all_vocab():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, word, meaning, example FROM vocab")
            return cursor.fetchall()
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("⚠️ Table 'vocab' not found. Returning empty list.")
            return []
        else:
            raise  # Any other DB error should be raised
    

