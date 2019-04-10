from django.urls import path
from . import views

urlpatterns = [
    path('drop_recreate/<env>/<type>', views.drop_recreate),
    path('reindex', views.reindex_all.as_view()),
]