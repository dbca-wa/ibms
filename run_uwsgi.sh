#!/bin/bash
exec uwsgi --ini uwsgi.ini --module ibms_project.wsgi
