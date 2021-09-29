from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from ibms.views import SiteHomeView, HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('healthcheck/', HealthCheckView.as_view(), name='health_check'),
    path('', include('ibms.urls')),
    path('', include('sfm.urls')),
    path('', SiteHomeView.as_view(), name='site_home'),
]
