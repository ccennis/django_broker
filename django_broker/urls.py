#!/usr/bin/env python

from django.urls import include, path
from . import views

urlpatterns = [
    path('broker/', include('reindex.urls')),
    path('broker/', include('rebuild.urls')),
    path('', views.hello_world, name='hello'),
]
