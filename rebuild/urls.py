from django.urls import path
from . import views

urlpatterns = [
    #individual get rebuild command
    path('rebuild/<env>/<type>/<dev_domain>/<id>', views.queue_rebuild),
    #post ids update many
    path('ids', views.rebuild_ids.as_view()),
]