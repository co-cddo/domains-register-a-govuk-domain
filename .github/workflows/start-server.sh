#!/bin/sh
echo "Starting test server"
export SECRET_KEY=blah
export DATABASE_URL=postgresql://govuk_domain:govuk_domain@localhost:5432/gov
poetry run ./manage.py runserver > /dev/null
