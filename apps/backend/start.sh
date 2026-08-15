#!/bin/sh
# Run database migrations
echo "Running alembic database migrations..."
alembic upgrade head

# Start application
echo "Starting FastAPI backend application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
