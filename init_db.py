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
import sys
from sqlalchemy.exc import ProgrammingError, OperationalError, SQLAlchemyError
from dotenv import load_dotenv
from app import create_app, db
from app.models.user import User

# Load environment variables
load_dotenv()

def init_db():
    """Initialize the database with a default admin user"""
    app = create_app()
    
    # Count connection attempts
    attempts = 0
    max_attempts = 5
    
    with app.app_context():
        while attempts < max_attempts:
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
                
                # Break out of the retry loop on success
                break
                
            except (ProgrammingError, OperationalError) as e:
                # If tables don't exist, try running migrations
                print(f"Error: {str(e)}")
                print("Tables don't exist yet. Run migrations first.")
                return
            except SQLAlchemyError as e:
                # Handle connection errors with retries
                attempts += 1
                if attempts >= max_attempts:
                    print(f"Failed to connect to database after {max_attempts} attempts.")
                    print(f"Last error: {str(e)}")
                    return
                
                print(f"Database connection error: {str(e)}")
                print(f"Retrying in 5 seconds... (Attempt {attempts}/{max_attempts})")
                time.sleep(5)


if __name__ == "__main__":
    init_db() 