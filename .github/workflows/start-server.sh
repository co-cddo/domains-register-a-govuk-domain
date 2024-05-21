#!/bin/sh
DEBUG=False
echo "Starting test server with DEBUG set to ${DEBUG}"
poetry run ./manage.py runserver 0.0.0.0:8010 >/dev/null 2>&1
