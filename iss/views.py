import locale

from django.http import JsonResponse
from django.shortcuts import render

from .utils import iss_orbit_calc, get_info_api

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')


def info(request):
    data = get_info_api()
    velo = float(data[0])
    velo_formatted = locale.format_string("%d", velo, grouping=True)
    alti = float(data[1])
    alti_formatted = locale.format_string("%d", alti, grouping=True)
    lat = data[3]
    lon = data[4]
    visi = data[2]

    return render(request, 'iss/pages/info-home.html', context={
        "velo": velo_formatted,
        "alti": alti_formatted,
        "visi": visi,
        "lat": lat,
        "lon": lon
    })


def home(request):
    return render(request, "iss/pages/home.html")


def iss_orbit(request):
    latlons = iss_orbit_calc()

    return JsonResponse({"path": latlons})