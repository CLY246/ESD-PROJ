#!/bin/sh

echo "Starting OrderManagement service..."

# Start the Flask app via Gunicorn
exec gunicorn ordermanagement:app -b 0.0.0.0:5000 --workers=1 --timeout 300
