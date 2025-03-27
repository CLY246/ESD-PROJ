#!/bin/sh

echo "Starting OrderManagement service..."



#!/bin/sh
exec gunicorn -b 0.0.0.0:5000 ordermanagement:app
