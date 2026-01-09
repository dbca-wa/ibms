# syntax=docker/dockerfile:1
FROM dhi.io/python:3.13-debian13-dev@sha256:afbe9dc3a5482aa5a10a1b3f6b169d71cfb0565d6ca223279af3c60696ae1cbe AS build-stage
LABEL org.opencontainers.image.authors=asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source=https://github.com/dbca-wa/ibms

# Copy and configure uv, to install dependencies
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/
WORKDIR /app
# Install project dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group dev --link-mode=copy --compile-bytecode --no-python-downloads --frozen \
  # Remove uv after use
  && rm -rf /bin/uv \
  && rm uv.lock

# Copy the remaining project files to finish building the project
COPY gunicorn.py manage.py ./
COPY ibms_project ./ibms_project
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
# Compile scripts and collect static files
RUN python -m compileall ibms_project \
  && python manage.py collectstatic --noinput

# Run project as the nonroot user
USER nonroot
EXPOSE 8080
CMD ["gunicorn", "ibms_project.wsgi", "--config", "gunicorn.py"]

##################################################################################

# FROM dhi.io/python:3.13 AS runtime-stage
# LABEL org.opencontainers.image.authors=asi@dbca.wa.gov.au
# LABEL org.opencontainers.image.source=https://github.com/dbca-wa/ibms
#
# # Copy over the built project and virtualenv
# WORKDIR /app
# COPY --from=build-stage /app /app
#
# # Image runs as the nonroot user
# ENV PYTHONUNBUFFERED=1
# ENV PATH="/app/.venv/bin:$PATH"
# EXPOSE 8080
# CMD ["gunicorn", "ibms_project.wsgi", "--config", "gunicorn.py"]
