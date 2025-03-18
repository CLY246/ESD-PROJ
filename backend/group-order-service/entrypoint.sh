#!/bin/sh
echo "Running database migrations..."
flask db upgrade  # Automatically runs migrations before starting Flask

echo "Starting Flask application..."
exec gunicorn -b 0.0.0.0:5000 grouporder:app 
