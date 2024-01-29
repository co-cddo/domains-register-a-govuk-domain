up-devserver:
	docker compose up -d

down-devserver:
	docker compose down

migrate-devserver:
	docker exec -it domains-register-a-govuk-domain-web-1 ./manage.py migrate