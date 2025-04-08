FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script first and make it executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p instance/uploads

# Expose port - will be overridden by $PORT on Render
EXPOSE 8000

# Start application
CMD ["/app/entrypoint.sh"] 