from django.conf import settings


def standard(request):
    '''
    Define a dictionary of context variables to pass to every template.
    '''
    context = {
        'page_title': settings.SITE_TITLE,
        'site_title': settings.SITE_TITLE,
        'site_acronym': settings.SITE_ACRONYM,
        'application_version_no': settings.APPLICATION_VERSION_NO,
        'user_navbar': 'ibms/user_navbar_li.html',
        'confluence_url': settings.CONFLUENCE_URL,
    }
    return context
