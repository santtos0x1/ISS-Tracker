from django.urls import path
from . import views

urlpatterns = [
    path('info/', views.info, name='info'),
    path("iss/info/", views.iss_info, name="iss_info")
]