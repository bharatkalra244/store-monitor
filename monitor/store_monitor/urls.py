from django.urls import path
from . import views

urlpatterns = [
    path('trigger_report/',views.triggerReport),
    path('get_report/', views.getReport)
]