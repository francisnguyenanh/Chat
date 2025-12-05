"""
Script to upgrade existing database with new columns
Run this if you already have chat.db
"""
from app import app, db
from models import Message
import sqlite3

def upgrade_database():
    """Add new columns to existing database"""
    with app.app_context():
        try:
            # Add edited_at column if doesn't exist
            db.session.execute('ALTER TABLE messages ADD COLUMN edited_at DATETIME')
            print('✓ Added edited_at column')
        except:
            print('- edited_at column already exists')
        
        try:
            # Add reactions column if doesn't exist
            db.session.execute("ALTER TABLE messages ADD COLUMN reactions TEXT DEFAULT '{}'")
            print('✓ Added reactions column')
        except:
            print('- reactions column already exists')
        
        db.session.commit()
        print('\n✅ Database upgrade completed!')

if __name__ == '__main__':
    upgrade_database()
