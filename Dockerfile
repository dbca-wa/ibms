# Prepare the base environment.
FROM python:3.10.12-slim-bookworm as builder_base_ibms
MAINTAINER asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source https://github.com/dbca-wa/ibms

RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y python3-dev libpq-dev gcc \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip

# Install Python libs using Poetry.
FROM builder_base_ibms as python_libs_ibms
WORKDIR /app
ENV POETRY_VERSION=1.5.1
RUN pip install "poetry==$POETRY_VERSION"
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Install the project.
FROM python_libs_ibms
COPY manage.py gunicorn.py ./
COPY ibms_project ./ibms_project
RUN python manage.py collectstatic --noinput
# Run the application as the www-data user.
USER www-data
EXPOSE 8080
CMD ["gunicorn", "ibms_project.wsgi", "--config", "gunicorn.py"]
