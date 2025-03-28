"""
Initialize the database with a default admin user.
Run this script after creating the database and running migrations:
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    python init_db.py
"""

import os
import time
from sqlalchemy.exc import ProgrammingError, OperationalError
from dotenv import load_dotenv
from app import create_app, db
from app.models.user import User

# Load environment variables
load_dotenv()

def init_db():
    """Initialize the database with a default admin user"""
    app = create_app()
    with app.app_context():
        # Make sure tables exist
        try:
            # Check if users table exists by trying to query it
            user_count = User.query.count()
            
            # If we got here, the table exists
            if user_count == 0:
                # Create admin user
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    role="admin",
                    first_name="Admin",
                    last_name="User"
                )
                admin.password = "admin123"  # This will be hashed
                
                # Add to database
                db.session.add(admin)
                db.session.commit()
                
                print("Admin user created: admin@example.com / admin123")
            else:
                print("Users already exist, skipping admin creation")
                
        except (ProgrammingError, OperationalError) as e:
            # If we get here, the tables don't exist yet
            print("Tables don't exist yet. Run migrations first.")
            print(f"Error: {str(e)}")
            return

if __name__ == "__main__":
    init_db() 