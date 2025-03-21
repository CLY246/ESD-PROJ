#!/bin/sh
# export FLASK_APP=grouporder.py 

# echo "Running database migrations..."
# flask db upgrade 

echo "Starting Flask SocketIO application..."
exec gunicorn grouporder:gunicorn_app --bind 0.0.0.0:5000 --worker-class eventlet --timeout 300

