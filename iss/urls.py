from django.urls import path
from iss.views import home

urlpatterns = [
    path('', home)
]