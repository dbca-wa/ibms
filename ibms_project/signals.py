from django.dispatch import Signal, receiver

# Signal used when getting the current user. Receivers should return a tuple of (user, priority).
current_user_getter = Signal()

# Signal used when setting current user. Takes one keyword argument: 'user'.
# Receivers should store the current user as needed. Return values are ignored.
current_user_setter = Signal()


@receiver(current_user_getter)
def _get_current_user_from_request(sender, **kwargs):
    """
    Signal handler to retrieve current user from request.
    """
    from .middleware import get_current_request

    return (getattr(get_current_request(), "user", False), -10)


@receiver(current_user_getter)
def _get_current_user_from_thread_locals(sender, **kwargs):
    """
    Signal handler to retrieve current user from thread locals.
    """
    from .middleware import _thread_locals

    return (getattr(_thread_locals, "user", False), 10)


@receiver(current_user_setter)
def _set_current_user_on_request(sender, **kwargs):
    """
    Signal handler to store current user to request.
    """
    from .middleware import get_current_request

    request = get_current_request()
    if request:
        request.user = kwargs["user"]


@receiver(current_user_setter)
def _set_current_user_on_thread_locals(sender, **kwargs):
    """
    Signal handler to store current user on thread locals.
    """
    from .middleware import _thread_locals

    _thread_locals.user = kwargs["user"]
