from django.urls import path
from . import views

app_name = 'iss'

urlpatterns = [
    path('', views.home, name='home'),
    path('iss/orbit/', views.iss_orbit, name='orbit'),
    path('iss/data/', views.info, name='data')
]