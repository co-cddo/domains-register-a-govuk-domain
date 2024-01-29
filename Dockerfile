FROM public.ecr.aws/docker/library/python:3.10

ARG POETRY_ARGS="--no-root --no-ansi --only main"

WORKDIR /srv/request_a_govuk_domain

RUN pip install poetry gunicorn \
  && useradd -u 1000 govuk_domain

COPY pyproject.toml poetry.lock /srv/request_a_govuk_domain/

RUN poetry config virtualenvs.create false \
  && poetry install ${POETRY_ARGS}

COPY manage.py /srv/request_a_govuk_domain/
COPY request_a_govuk_domain /srv/request_a_govuk_domain/request_a_govuk_domain

RUN sed -i 's/\r$//' /srv/request_a_govuk_domain/manage.py  && \
        chmod +x /srv/request_a_govuk_domain/manage.py

RUN SECRET_KEY=unneeded /srv/request_a_govuk_domain/manage.py collectstatic --no-input

RUN mkdir /var/run/request_a_govuk_domain \
  && chown govuk_domain:govuk_domain /var/run/request_a_govuk_domain

USER govuk_domain
EXPOSE 8000
