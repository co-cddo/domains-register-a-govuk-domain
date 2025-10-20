FROM public.ecr.aws/amazonlinux/amazonlinux:2023

ARG POETRY_ARGS="--no-root --no-ansi --only main"

# shadow-utils is needed for useradd command used below
RUN dnf -y install python3.12 python3.12-devel python3-pip shadow-utils && \
    ln -s /usr/bin/python3.12 /usr/bin/python && \
    python3.12 -m ensurepip && \
    pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN useradd -u 1000 -m govuk_domain

RUN pip install --no-cache-dir poetry gunicorn

COPY pyproject.toml poetry.lock /app/

WORKDIR /app

RUN poetry config virtualenvs.create false && \
    poetry install ${POETRY_ARGS}

COPY manage.py /app/
COPY request_a_govuk_domain /app/request_a_govuk_domain

RUN sed -i 's/\r$//' /app/manage.py && \
    chmod +x /app/manage.py

ENV SECRET_KEY=unneeded
ENV DOMAIN_NAME=http://localhost:2010

RUN /app/manage.py collectstatic --no-input

RUN mkdir /var/run/request_a_govuk_domain && \
    chown govuk_domain:govuk_domain /var/run/request_a_govuk_domain

USER govuk_domain

EXPOSE 8010
