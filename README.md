# Integrated Business Management System

This project consists of the Integrated Business Management System
(IBMS) corporate application, used by the Department of Biodiversity,
Conservation and Attractions.

# Installation

The recommended way to set up this project for development is using
[Poetry](https://python-poetry.org/docs/) to install and manage a virtual Python
environment. With Poetry installed, change into the project directory and run:

    poetry install

To run Python commands in the virtualenv, thereafter run them like so:

    poetry run python manage.py

Manage new or updating project dependencies with Poetry also, like so:

    poetry add newpackage==1.0

# Environment variables

This project uses environment variables (in a `.env` file) to define application settings.
Required settings are as follows:

    DATABASE_URL="postgis://USER:PASSWORD@HOST:PORT/DATABASE_NAME"
    SECRET_KEY="ThisIsASecretKey"

# Running

Use `runserver` to run a local copy of the application:

    poetry run python manage.py runserver 0:8080

Run console commands manually:

    poetry run python manage.py shell_plus

# Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/ibms .

# Pre-commit hooks

This project includes the following pre-commit hooks:

- TruffleHog: https://docs.trufflesecurity.com/docs/scanning-git/precommit-hooks/

Pre-commit hooks may have additional system dependencies to run. Optionally
install pre-commit hooks locally like so:

    poetry run pre-commit install

Reference: https://pre-commit.com/
