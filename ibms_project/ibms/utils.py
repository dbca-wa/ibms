from datetime import datetime
from ibms.models import GLPivDownload


def get_download_period():
    """Return the 'newest' download_period date value for all the GLPivDownload objects.
    """
    if not GLPivDownload.objects.exists():
        return datetime.today()
    elif not GLPivDownload.objects.filter(download_period__isnull=False).exists():
        return datetime.today()
    return GLPivDownload.objects.order_by('-download_period').first().download_period
