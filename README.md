# DataRoom Backend API

Flask API backend with PostgreSQL database for the DataRoom application.

## Super Simple Docker Setup

Start the containers:

```bash
docker-compose up -d
```

The backend will run on http://localhost:8000 with auto-reload enabled.

## Manual Database Setup

Since we're not automatically initializing the database, you need to do this manually:

```bash
# Connect to the backend container
docker exec -it backend bash

# Then inside the container run:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python init_db.py
```

## Accessing the PostgreSQL Database

You can connect to the PostgreSQL database directly:

```bash
# Connect to the database container
docker exec -it dataroom_db bash

# Connect with psql
psql -U postgres dataroom

# Or from your host if you have psql installed
psql -h localhost -p 5432 -U postgres dataroom
```

The database credentials are:
- Host: localhost
- Port: 5432
- User: postgres
- Password: postgres
- Database: dataroom

## API Documentation

### Authentication

- **POST /api/users/register** - Register a new user
- **POST /api/users/login** - Login and get authentication token

All other endpoints require authentication via Bearer token in the Authorization header.

### Users

- **GET /api/users/me** - Get current user profile
- **GET /api/users/:id** - Get user by ID
- **PUT /api/users/:id** - Update user profile
- **GET /api/users** - Get all users (admin only)
- **DELETE /api/users/:id** - Delete user (admin only)

### Documents

- **GET /api/documents** - Get all documents with pagination
- **GET /api/documents/:id** - Get document by ID
- **POST /api/documents** - Create a new document (multipart/form-data)
- **PUT /api/documents/:id** - Update document
- **DELETE /api/documents/:id** - Delete document
- **GET /api/documents/:id/download** - Download document file
- **GET /api/documents/search?q=query** - Search documents by title, description or tags