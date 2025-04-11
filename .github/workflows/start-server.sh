#!/bin/sh
DEBUG=False
export TEST_CSP=yes
echo "Starting test server with DEBUG set to ${DEBUG}"
curl --request GET -sL \
     --url 'http://localhost:9090/favicon.ico'
GOOGLE_ANALYTICS_ID=GTM-TEST poetry run ./manage.py runserver 0.0.0.0:8010
