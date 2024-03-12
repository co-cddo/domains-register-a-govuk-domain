#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py loaddata ./seed/reviewer_group.json ./seed/users.json ./seed/request.json
