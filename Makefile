up:
	docker compose -f docker-compose.yml run --rm --service-ports web

up-devserver:
	docker compose -f docker-compose.yml run --rm --service-ports --entrypoint "python manage.py runserver 0.0.0.0:8000" web

up-devserver-nodebug:
	docker compose -f docker-compose.yml run --rm --service-ports --env DEBUG=False --entrypoint "python manage.py runserver 0.0.0.0:8000" web

down:
	docker compose down

build:
	docker compose build

shell:
	docker compose exec web bash

collectstatic:
	docker compose -f docker-compose.yml run --rm --service-ports --entrypoint "python manage.py collectstatic --noinput" web

makemigrations:
	docker compose run --entrypoint "python manage.py makemigrations" web

migrate-devserver:
	docker exec -it `docker ps --format '{{.Names}}' | grep web` ./manage.py migrate

clear-db:
	docker compose down && docker container prune -f && docker volume rm domains-register-a-govuk-domain_postgres-data

test:
	docker compose run --rm --service-ports --entrypoint "python manage.py test -v 2" web

create-sample-data:
	docker compose exec web bash -c "python manage.py create_sample_data"
