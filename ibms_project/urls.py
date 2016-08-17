from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic import RedirectView
from ibms.views import SiteHomeView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login, name='login', kwargs={'template_name': 'login.html'}),
    url(r'^logout/$', logout, name='logout', kwargs={'template_name': 'logged_out.html'}),
    url(r'^confluence', RedirectView.as_view(url=settings.HELP_URL), name='help_page'),
    url(r'', include('ibms.urls')),
    url(r'', include('sfm.urls')),
    url(r'^$', SiteHomeView.as_view(), name='site_home'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
