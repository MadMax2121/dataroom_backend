#!/bin/bash

# Set default port if not provided
PORT=${PORT:-8000}

if [ "$FLASK_ENV" = "production" ]; then
  echo "Running in production mode on port $PORT"
  gunicorn --bind 0.0.0.0:$PORT "app:create_app()"
else
  echo "Running in development mode on port $PORT"
  flask run --host=0.0.0.0 --port=$PORT
fi
