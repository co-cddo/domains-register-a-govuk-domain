#!/bin/sh
echo "Starting test server"
export DEBUG=False
poetry run ./manage.py runserver > /dev/null
