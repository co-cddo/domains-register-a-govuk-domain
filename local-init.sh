#!/bin/bash

python manage.py makemigrations
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py create_reviewer_group
python manage.py loaddata ./request_a_govuk_domain/admin-theme/admin-theme.json
python manage.py loaddata ./seed/users.json
python manage.py add_initial_registrars
python manage.py create_sample_data
