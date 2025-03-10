FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory for SQLite
RUN mkdir -p /app/data

# Copy application code
COPY app/ /app/app/

# Run the application
CMD ["python", "-m", "app.main"]

