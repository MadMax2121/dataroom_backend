import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    if test_config is None:
        # Load the instance config from environment variables
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev"),
            UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", "instance/uploads"),
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, "uploads"), exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.routes import users, documents, folders
    app.register_blueprint(users.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(folders.bp)
    
    # A simple route to confirm the app is working
    @app.route("/api/health")
    def health_check():
        return {"status": "healthy", "message": "DataRoom API is running"}
    
    return app 