from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

from django.conf.urls import include

urlpatterns += [
    path('catalog/', include('catalog.urls')),
]