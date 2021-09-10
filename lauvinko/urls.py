from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^.*$', views.react_index, name="react_index")
]
