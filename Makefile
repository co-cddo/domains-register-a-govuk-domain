up:
	docker compose -f docker-compose.yml -f docker-compose-local.yml run --rm --service-ports web

up-devserver:
	docker compose -f docker-compose.yml -f docker-compose-local.yml run --rm --service-ports --entrypoint "python manage.py runserver 0.0.0.0:8000" web

down:
	docker compose down

build:
	docker compose build

collectstatic:
		docker compose -f docker-compose.yml -f docker-compose-local.yml run --rm --service-ports --entrypoint "python manage.py collectstatic --noinput" web

migrate-devserver:
	docker exec -it domains-register-a-govuk-domain-web-1 ./manage.py migrate
