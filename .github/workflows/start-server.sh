#!/bin/sh
echo "Starting test server"
poetry run ./manage.py runserver 0.0.0.0:8010 >/dev/null 2>&1
