from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import RedirectView
from ibms.views import SiteHomeView, HealthCheckView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='{}favicon.ico'.format(settings.STATIC_URL)), name='favicon'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('healthcheck/', HealthCheckView.as_view(), name='health_check'),
    path('', include('ibms.urls')),
    path('', include('sfm.urls')),
    path('', SiteHomeView.as_view(), name='site_home'),
]
