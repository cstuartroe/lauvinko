from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('page/<slug:name>', views.page_content, name="page_content"),
    path('api/gloss', views.gloss, name="gloss"),
    path('api/dict', views.dictionary, name="dictionary"),
    re_path(r'^.*$', views.react_index, name="react_index")
]
