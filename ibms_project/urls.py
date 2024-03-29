from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from ibms.views import SiteHomeView


admin.site.site_header = 'IBMS database administration'
admin.site.index_title = 'IBMS database'
admin.site.site_title = 'IBMS'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('', include('ibms.urls')),
    path('', include('sfm.urls')),
    path('', SiteHomeView.as_view(), name='site_home'),
]
