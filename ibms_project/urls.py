from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView
from ibms.views import SiteHomeView, HealthCheckView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    url(r'^confluence', RedirectView.as_view(url=settings.HELP_URL), name='help_page'),
    url(r'^healthcheck/$', HealthCheckView.as_view(), name='health_check'),
    url(r'', include('ibms.urls')),
    url(r'', include('sfm.urls')),
    url(r'^$', SiteHomeView.as_view(), name='site_home'),
]
