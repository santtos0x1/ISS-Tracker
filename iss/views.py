import datetime
import math

import requests
from django.http import JsonResponse
from django.shortcuts import render
from sgp4.api import Satrec, jday

cached_tle = None
cached_time = None
CACHE_DURATION = datetime.timedelta(minutes=30)  # suggest smaller cache


def home(request):
    return render(request, "iss/pages/home.html")


def get_tle():
    global cached_tle, cached_time
    now = datetime.datetime.utcnow()

    if not cached_tle or (now - cached_time) > CACHE_DURATION:
        tle_url = "https://celestrak.org/NORAD/elements/stations.txt"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(tle_url, headers=headers)
        tle_data = resp.text.splitlines()
        # search for ISS (more robust than fixed indices)
        for i, line in enumerate(tle_data):
            if "ISS" in line.upper() or "ZARYA" in line.upper():
                line1 = tle_data[i+1].strip()
                line2 = tle_data[i+2].strip()
                cached_tle = (line1, line2)
                cached_time = now
                break
        else:
            # fallback to first lines if not found
            line1, line2 = tle_data[1].strip(), tle_data[2].strip()
            cached_tle = (line1, line2)
            cached_time = now

    return cached_tle

def gmst_from_jd(jd, fr):
    """
    Compute Greenwich Mean Sidereal Time in radians.
    Based on Vallado (2007) algorithm (seconds -> radians).
    """
    # full Julian date (days)
    jd_full = jd + fr
    T = (jd_full - 2451545.0) / 36525.0
    # GMST in seconds
    gmst_sec = 67310.54841 + (876600.0 * 3600 + 8640184.812866) * T \
               + 0.093104 * (T**2) - 6.2e-6 * (T**3)
    # normalize to [0,86400)
    gmst_sec = gmst_sec % 86400.0
    # convert seconds to radians: 360 deg = 86400 sec -> 1 sec = 360/86400 deg
    gmst_deg = gmst_sec * (360.0 / 86400.0)
    gmst_rad = math.radians(gmst_deg)
    return gmst_rad


def teme_to_ecef(r_teme, jd, fr):
    """Rotate TEME vector to ECEF using GMST (approx.)."""
    gmst = gmst_from_jd(jd, fr)
    x, y, z = r_teme
    # rotation about Z by +GMST (TEME->ECEF)
    x_ecef =  math.cos(gmst)*x + math.sin(gmst)*y
    y_ecef = -math.sin(gmst)*x + math.cos(gmst)*y
    z_ecef = z
    return x_ecef, y_ecef, z_ecef


def ecef_to_latlon(x, y, z):
    """Convert ECEF (km) to geodetic lat/lon (approx, ignoring ellipsoid height)."""
    # Simple spherical conversion (adequate for visualization). For highest precision, use WGS84 ellipsoid formulas.
    r = math.sqrt(x*x + y*y + z*z)
    lat = math.degrees(math.asin(z / r))
    lon = math.degrees(math.atan2(y, x))
    # Normalize lon to [-180, 180)
    lon = (lon + 180) % 360 - 180
    return lat, lon


def iss_orbit(request):
    line1, line2 = get_tle()
    sat = Satrec.twoline2rv(line1, line2)

    now = datetime.datetime.utcnow()
    latlons = []

    # The time of the orbit and the step changes the orbit line - Verify -
    # calculate for ~1.5 orbits (0..5700 s) with 60s step (or adjust)
    for t in range(0, 5700, 30):
        future = now + datetime.timedelta(seconds=t)

        jd, fr = jday(future.year, future.month, future.day,
                      future.hour, future.minute, future.second + future.microsecond*1e-6)
        e, r, v = sat.sgp4(jd, fr)

        if e == 0:
            # r is in km in TEME frame
            x_teme, y_teme, z_teme = r
            # convert TEME -> ECEF
            x_ecef, y_ecef, z_ecef = teme_to_ecef((x_teme, y_teme, z_teme), jd, fr)
            # convert ECEF -> lat/lon
            lat, lon = ecef_to_latlon(x_ecef, y_ecef, z_ecef)
            latlons.append([lat, lon])

    return JsonResponse({"path": latlons})