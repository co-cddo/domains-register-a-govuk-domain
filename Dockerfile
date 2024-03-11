FROM public.ecr.aws/docker/library/python:3.10

ARG POETRY_ARGS="--no-root --no-ansi --only main"

RUN useradd -u 1000 govuk_domain

RUN pip install poetry gunicorn

COPY pyproject.toml poetry.lock /app/

WORKDIR /app

RUN poetry config virtualenvs.create false && \
    poetry install ${POETRY_ARGS}

COPY manage.py /app/
COPY request_a_govuk_domain /app/request_a_govuk_domain

RUN sed -i 's/\r$//' /app/manage.py  && \
    chmod +x /app/manage.py

RUN SECRET_KEY=unneeded /app/manage.py collectstatic --no-input

RUN mkdir /var/run/request_a_govuk_domain && \
    chown govuk_domain:govuk_domain /var/run/request_a_govuk_domain

RUN mkdir /home/govuk_domain && \
    chown govuk_domain:govuk_domain /home/govuk_domain

USER govuk_domain

EXPOSE 8000
