from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from ibms.views import SiteHomeView

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login',
        kwargs={'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout',
        kwargs={'template_name': 'logged_out.html'}),
    url(r'^confluence', RedirectView.as_view(url=settings.HELP_URL), name='help_page'),
    (r'', include('ibms.urls')),
    (r'', include('sfm.urls')),
    url(r'^$', SiteHomeView.as_view(), name='site_home'),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
