#!/bin/sh
DEBUG=False
export TEST_CSP=yes
echo "Starting test server with DEBUG set to ${DEBUG} and TEST_CSP set to ${TEST_CSP}"
GOOGLE_ANALYTICS_ID=GTM-TEST poetry run ./manage.py runserver 0.0.0.0:8010
