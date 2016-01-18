"""
WSGI config for IBMS project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import confy
from django.core.wsgi import get_wsgi_application
from dj_static import Cling


confy.read_environment_file()
application = Cling(get_wsgi_application())
