# syntax=docker/dockerfile:1
# Prepare the base environment.
FROM python:3.12.4-slim AS builder_base_ibms
LABEL org.opencontainers.image.authors=asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source=https://github.com/dbca-wa/ibms

RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y python3-dev libpq-dev gcc \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --root-user-action=ignore --upgrade pip

# Install Python libs using Poetry.
FROM builder_base_ibms AS python_libs_ibms
WORKDIR /app
ARG POETRY_VERSION=1.8.3
RUN pip install --no-cache-dir --root-user-action=ignore poetry==${POETRY_VERSION}
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Create a non-root user.
ARG UID=10001
ARG GID=10001
RUN groupadd -g ${GID} appuser \
  && useradd --no-create-home --no-log-init --uid ${UID} --gid ${GID} appuser

# Install the project.
FROM python_libs_ibms
COPY manage.py gunicorn.py ./
COPY ibms_project ./ibms_project
RUN python manage.py collectstatic --noinput

USER ${UID}
EXPOSE 8080
CMD ["gunicorn", "ibms_project.wsgi", "--config", "gunicorn.py"]
