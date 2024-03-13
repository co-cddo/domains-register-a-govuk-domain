#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py create_reviewer_group
python manage.py loaddata ./seed/users.json ./seed/request.json
