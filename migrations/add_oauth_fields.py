"""Add OAuth fields to user table

This migration adds columns for OAuth authentication providers to the users table.
"""

from app import db
from flask import Flask
from flask_migrate import Migrate
import logging

def upgrade():
    """Add OAuth related columns to users table"""
    
    try:
        # Check if column already exists
        result = db.engine.execute("SELECT column_name FROM information_schema.columns "
                                  "WHERE table_name='users' AND column_name='oauth_google_id'")
        if not result.fetchone():
            db.engine.execute("ALTER TABLE users ADD COLUMN oauth_google_id VARCHAR(100) UNIQUE")
            print("Successfully added oauth_google_id column to users table")
        else:
            print("Column oauth_google_id already exists in users table")
    except Exception as e:
        logging.error(f"Error adding OAuth columns: {str(e)}")
        print(f"Error adding OAuth columns: {str(e)}")
        raise

def downgrade():
    """Remove OAuth related columns from users table"""
    
    try:
        # Check if column exists before dropping
        result = db.engine.execute("SELECT column_name FROM information_schema.columns "
                                  "WHERE table_name='users' AND column_name='oauth_google_id'")
        if result.fetchone():
            db.engine.execute("ALTER TABLE users DROP COLUMN IF EXISTS oauth_google_id")
            print("Successfully removed oauth_google_id column from users table")
        else:
            print("Column oauth_google_id does not exist in users table")
    except Exception as e:
        logging.error(f"Error removing OAuth columns: {str(e)}")
        print(f"Error removing OAuth columns: {str(e)}")
        raise

if __name__ == "__main__":
    # This allows running the migration script directly
    from app import create_app
    
    app = create_app()
    with app.app_context():
        upgrade() 