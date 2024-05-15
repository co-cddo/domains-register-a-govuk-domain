#!/bin/sh
echo "Starting test server with DEBUG set to False"
export DEBUG=False
poetry run ./manage.py runserver > /dev/null
