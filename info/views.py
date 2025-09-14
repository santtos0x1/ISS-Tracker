from django.shortcuts import render
from django.http import JsonResponse
import locale
import requests


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_info_api():
    ISS_URL = 'https://api.wheretheiss.at/v1/satellites/25544'
    req = requests.get(ISS_URL)
    data = req.json() 
    iss_lat = f"{data['latitude']}"
    iss_lon = f"{data['longitude']}"
    iss_velocity = f"{data['velocity']:.2f}"
    iss_altitude = f"{data['altitude']:.2f}"
    iss_visibility = f"{data['visibility']}" 
    info = [iss_velocity, iss_altitude, iss_visibility, iss_lat, iss_lon]
    
    return info


def info(request):
    data = get_info_api()
    velo = float(data[0])
    velo_formatted = locale.format_string("%d", velo, grouping=True)
    alti = float(data[1])
    alti_formatted = locale.format_string("%d", alti, grouping=True)
    lat = data[3]
    lon = data[4]
    visi = data[2]
    
    return render(request, 'info/pages/info-home.html', context={
        "velo": velo_formatted,
        "alti": alti_formatted,
        "visi": visi,
        "lat": lat,
        "lon": lon
    })


def iss_info(request):
    return JsonResponse({"inf": get_info_api()})