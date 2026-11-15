# Integrated Business Management System

This project consists of the Integrated Business Management System
(IBMS) corporate application, used by the Department of Biodiversity,
Conservation and Attractions.

## Installation

Dependencies for this project are managed using [uv](https://docs.astral.sh/uv/).
With uv installed, change into the project directory and run:

    uv sync

Activate the virtualenv like so:

    source .venv/bin/activate

To run Python commands in the activated virtualenv, thereafter run them like so:

    python manage.py

Manage new or updated project dependencies with uv also, like so:

    uv add newpackage==1.0

## Environment variables

This project uses environment variables (in a `.env` file) to define application settings.
Required settings are as follows:

    DATABASE_URL="postgis://USER:PASSWORD@HOST:PORT/DATABASE_NAME"
    SECRET_KEY="ThisIsASecretKey"

## Running

Use `runserver` to run a local copy of the application:

    python manage.py runserver 0:8080

Run console commands manually:

    python manage.py shell_plus

Run the asynchronous task worker:

    python manage.py db_worker

## Testing

Run unit tests as follows:

    python manage.py test --keepdb -v2 --failfast

To obtain test coverage:

    coverage run --source='.' manage.py test --keepdb -v2 --failfast
    coverage report -m

## Docker image

Builds are defined in `docker-bake.hcl`. To build a local image for your
native platform and load it into Docker:

    docker buildx bake local

Run the image locally in a container like so:

    docker container run --rm -p 8080:8080 --env-file .env ghcr.io/dbca-wa/ibms:dev

To build and push a multi-arch image manually (without waiting for CI, requires `--push`):

    TAG=v1.2.3 docker buildx bake --push app

## Pre-commit hooks

This project includes the following pre-commit hooks:

- TruffleHog: <https://docs.trufflesecurity.com/docs/scanning-git/precommit-hooks/>

Pre-commit hooks may have additional system dependencies to run. Optionally
install pre-commit hooks locally like so:

    pre-commit install

Reference: <https://pre-commit.com/>
