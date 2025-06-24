import logging
import threading

from django.db import connections
from django.http import HttpResponse, HttpResponseServerError

LOGGER = logging.getLogger("ibms")
_thread_locals = threading.local()


class HealthCheckMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            if request.path == "/readyz":
                return self.readiness(request)
            elif request.path == "/livez":
                return self.liveness(request)
        return self.get_response(request)

    def liveness(self, request):
        """Returns that the server is alive."""
        return HttpResponse("OK")

    def readiness(self, request):
        """Connect to each database and do a generic standard SQL query
        that doesn't write any data and doesn't depend on any tables
        being present.
        """
        try:
            cursor = connections["default"].cursor()
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            cursor.close()
            if row is None:
                return HttpResponseServerError("Database: invalid response")
        except Exception as e:
            LOGGER.exception(e)
            return HttpResponseServerError("Database: unable to connect")

        return HttpResponse("OK")


def get_current_user(_return_false=False):
    """Return the user associated with the current request thread."""
    from .signals import current_user_getter

    top_priority = -9999
    top_user = False if _return_false else None
    results = current_user_getter.send_robust(get_current_user)

    for receiver, response in results:
        priority = 0
        if isinstance(response, Exception):
            LOGGER.exception(f"{receiver} raised exception: {response}")
            continue
        elif isinstance(response, (tuple, list)) and response:
            user = response[0]
            if len(response) > 1:
                priority = response[1]
        elif response or response in (None, False):
            user = response
        else:
            LOGGER.error(f"{receiver} returned invalid response: {response}")
            continue
        if user is not False:
            if priority > top_priority:
                top_priority = priority
                top_user = user

    return top_user


def set_current_user(user=None):
    """Update the user associated with the current request thread."""
    from .signals import current_user_setter

    results = current_user_setter.send_robust(set_current_user, user=user)

    for receiver, response in results:
        if isinstance(response, Exception):
            LOGGER.exception(f"{receiver} raised exception: {response}")


def get_current_request():
    """Return the request associated with the current thread."""
    return getattr(_thread_locals, "request", None)


def set_current_request(request=None):
    """Update the request associated with the current thread."""
    _thread_locals.request = request

    # Clear the current user if also clearing the request.
    if not request:
        set_current_user(False)


class CurrentRequestUserMiddleware(object):
    """Middleware to capture the request and user from the current thread."""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):  # pragma: no cover
        response = self.process_request(request)
        try:
            response = self.get_response(request)
        except Exception as e:
            self.process_exception(request, e)
            raise
        return self.process_response(request, response)

    def process_request(self, request):
        set_current_request(request)

    def process_response(self, request, response):
        set_current_request(None)
        return response

    def process_exception(self, request, exception):
        set_current_request(None)
