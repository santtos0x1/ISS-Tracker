import datetime
import math

import requests
from django.http import JsonResponse
from django.shortcuts import render
from sgp4.api import Satrec, jday


cached_tle = None
cached_time = None
CACHE_DURATION = datetime.timedelta(hours=2)


def home(request):
    return render(request, "iss/pages/home.html")


def get_tle():
    global cached_tle, cached_time
    now = datetime.datetime.utcnow()
    
    # Se não tem cache ou passou mais de 2h, atualiza
    if not cached_tle or (now - cached_time) > CACHE_DURATION:
        tle_url = "https://celestrak.org/NORAD/elements/stations.txt"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(tle_url, headers=headers)
        tle_data = resp.text.splitlines()
        line1, line2 = tle_data[1], tle_data[2]
        cached_tle = (line1, line2)
        cached_time = now
    
    return cached_tle


def iss_orbit(request):
    line1, line2 = get_tle()
    sat = Satrec.twoline2rv(line1, line2)

    now = datetime.datetime.utcnow()
    latlons = []

    for t in range(0, 5700, 60): 
        future = now + datetime.timedelta(seconds=t)
        
        jd, fr = jday(future.year, future.month, future.day,
                      future.hour, future.minute, future.second + future.microsecond*1e-6)
        e, r, v = sat.sgp4(jd, fr)
        
        if e == 0:
            x, y, z = r
            lat = math.degrees(math.atan2(z, (x**2 + y**2)**0.5))
            lon = math.degrees(math.atan2(y, x))
            lon = (lon + 180) % 360 - 180
            latlons.append([lat, lon])

    return JsonResponse({"path": latlons})