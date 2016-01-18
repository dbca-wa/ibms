from datetime import datetime
import functools
import re
import warnings

from ibms.models import GLPivDownload


def unique_list_items(li):
    checked = []
    for i in li:
        if i not in checked:
            checked.append(i)
    return checked


def get_download_period():
    # Handle edge case (for testing)
    if not GLPivDownload.objects.exists():
        return datetime.today()
    dates = [datetime.strptime(x[0], "%d/%m/%Y") for x in
             GLPivDownload.objects.order_by("-id")[:1000].values_list(
                 "downloadPeriod")]
    dates.sort()
    return dates[-1].date()


def getdict(d, pref):
    """Parse brackets into dicts in POST queries.
    """
    r = re.compile(r'^%s\[(.*)\]$' % pref)
    return dict((r.sub(r'\1', k), v) for (k, v) in d.iteritems() if r.match(k))


def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)
    return new_func


def breadcrumb_trail(links, sep=' > '):
    """
    ``links`` must be a list of two-item tuples in the format (URL, Text).
    URL may be None, in which case the trail will contain the Text only.
    Returns a string of HTML.
    """
    trail = ''
    url_str = '<a href="{0}">{1}</a>'
    # Iterate over the list, except for the last item.
    for i in links[:-1]:
        if i[0]:
            trail += url_str.format(i[0], i[1]) + sep
        else:
            trail += i[1] + sep
    # Add the list item on the list to the trail.
    if links[-1][0]:
        trail += url_str.format(links[-1][0], links[-1][1])
    else:
        trail += links[-1][1]
    return trail
