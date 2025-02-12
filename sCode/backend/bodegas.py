import sqlite3
import uuid
import os
import subprocess
#import datetime import datetime

DB_path = "/Users/fernandocarrillo/blue42/database/bodega_directory.db"

def connect_db():
    conn = sqlite3.connect(DB_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bodegas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bodega_id TEXT UNIQUE NOT NULL,
                        enterprise_name TEXT NOT NULL,
                        compute_instance TEXT NOT NULL,
                        storage_path TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    return conn

