from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('iss/orbit/', views.iss_orbit, name='iss_orbit')
]