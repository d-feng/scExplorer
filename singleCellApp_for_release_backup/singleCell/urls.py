

from django.contrib import admin
from django.urls import include,path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')),
]


urlpatterns += staticfiles_urlpatterns()
