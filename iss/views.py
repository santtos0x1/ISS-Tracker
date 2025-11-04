from django.http import JsonResponse
from django.shortcuts import render

from .utils import iss_orbit_calc, get_info_api


def info(request):
    data = get_info_api()

    return render(request, 'iss/pages/info-home.html', context={
        "velo": data.get('velocity'),
        "alti": data.get('altitude'),
        "visi": data.get('visibility'),
        "lat": data.get('lat'),
        "lon": data.get('lon')
    })


def home(request):
    return render(request, "iss/pages/home.html")


def iss_orbit(request):
    latlons = iss_orbit_calc()

    return JsonResponse({"path": latlons})