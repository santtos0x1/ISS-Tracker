from django.urls import path
from . import views

app_name = 'iss'

urlpatterns = [
    path('', views.home, name='home'),
    path('data/', views.info, name='data'),
    path('orbit/data/json/', views.iss_orbit, name='orbit'),
]