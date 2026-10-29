FROM public.ecr.aws/amazonlinux/amazonlinux:2023

# Extra flags for `uv sync`
# docker-compose passes --all-groups for a dev image
ARG UV_SYNC_ARGS="--no-dev"

# shadow-utils is needed for useradd command used below
RUN dnf -y install python3.12 shadow-utils && \
    ln -s /usr/bin/python3.12 /usr/bin/python && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN useradd -u 1000 -m govuk_domain

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=/usr/bin/python3.12 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock /app/

WORKDIR /app

RUN uv sync --frozen --no-cache ${UV_SYNC_ARGS}

COPY manage.py /app/
COPY request_a_govuk_domain /app/request_a_govuk_domain

RUN sed -i 's/\r$//' /app/manage.py && \
    chmod +x /app/manage.py

ENV SECRET_KEY=unneeded
ENV DOMAIN_NAME=http://localhost:2010

RUN /app/manage.py collectstatic --no-input

VOLUME /tmp
RUN mkdir /var/run/request_a_govuk_domain && \
    chown govuk_domain:govuk_domain /var/run/request_a_govuk_domain

USER govuk_domain

EXPOSE 8010
