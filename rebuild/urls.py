from django.urls import path
from . import views

urlpatterns = [
    #individual get rebuild command
    path('rebuild', views.queue_rebuild.as_view()),
    #post ids update many
    path('rebuild/ids', views.rebuild_ids.as_view()),
]