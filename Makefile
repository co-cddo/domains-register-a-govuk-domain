up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs web -f

migrate-devserver:
	docker exec -it domains-register-a-govuk-domain-web-1 ./manage.py migrate