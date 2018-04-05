from datetime import datetime
from ibms.models import GLPivDownload


def get_download_period():
    # Handle edge case (for testing)
    if not GLPivDownload.objects.exists():
        return datetime.today()
    dates = [datetime.strptime(x[0], "%d/%m/%Y") for x in
             GLPivDownload.objects.order_by("-id")[:1000].values_list(
                 "downloadPeriod")]
    dates.sort()
    return dates[-1].date()


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
