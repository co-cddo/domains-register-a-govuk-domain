#!/bin/sh
echo "Starting test server"
poetry run ./manage.py runserver > /dev/null
