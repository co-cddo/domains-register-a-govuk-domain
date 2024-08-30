#!/bin/sh
DEBUG=False
echo "Starting test server with DEBUG set to ${DEBUG}"
GOOGLE_ANALYTICS_ID=GTM-TEST poetry run ./manage.py runserver 0.0.0.0:8010
