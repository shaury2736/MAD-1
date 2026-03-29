import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import DATABASE
from models import ALL_TABLES

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    db = get_db()
    db.executescript(';'.join(ALL_TABLES))

    # Seed admin if not exists
    existing_admin = db.execute('SELECT id FROM admin WHERE email=?', ('admin@iitm.ac.in',)).fetchone()
    if not existing_admin:
        db.execute('INSERT INTO admin (name, email, password) VALUES (?, ?, ?)',
                   ('Super Admin', 'admin@iitm.ac.in', generate_password_hash('admin123')))

    db.commit()
    db.close()
    print("Database initialized. Admin: admin@iitm.ac.in / admin123")

if __name__ == '__main__':
    init_db()
