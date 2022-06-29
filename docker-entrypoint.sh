#!/usr/bin/env bash
echo "Waiting for MySQL..."
cd /Photos-Docker-Flask
gunicorn --bind 0.0.0.0:5000 --timeout 180 --limit-request-fields 327680 --workers 3 --log-level DEBUG run:app 
