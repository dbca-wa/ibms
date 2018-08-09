FROM python:3.6.6-alpine
MAINTAINER asi@dbca.wa.gov.au

WORKDIR /usr/src/app
COPY manage.py requirements.txt gunicorn.ini ./
COPY ibms_project ./ibms_project
RUN apk update \
  && apk upgrade \
  && apk add --no-cache --virtual .build-deps postgresql-dev gcc python3-dev musl-dev \
  && apk add --no-cache libpq bash git \
  && pip install --no-cache-dir -r requirements.txt \
  && python manage.py collectstatic --noinput \
  && apk del .build-deps

EXPOSE 8080
CMD ["gunicorn", "ibms_project.wsgi", "--config", "gunicorn.ini"]
