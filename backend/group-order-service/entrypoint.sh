#!/bin/sh
echo "Running database migrations..."
flask db upgrade 

echo "Starting Flask application..."
exec gunicorn -b 0.0.0.0:5000 grouporder:app --worker-class eventlet --workers 1 --timeout 300
