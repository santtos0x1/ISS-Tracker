function splitPathAtDateLine(path) {
    let segments = [];
    let currentSegment = [];

    for (let i = 0; i < path.length; i++) {
        let [lat, lon] = path[i];
        if (lon > 180) lon -= 360;
        if (lon < -180) lon += 360;

        if (i > 0) {
            let [prevLat, prevLon] = path[i-1];
            if (prevLon > 180) prevLon -= 360;
            if (prevLon < -180) prevLon += 360;

            let lonDiff = Math.abs(lon - prevLon);

            if (lonDiff > 180) {
                if (currentSegment.length > 1) {
                    segments.push([...currentSegment]);
                }
                currentSegment = [];
            }
        }
        currentSegment.push([lat, lon]);
    }

    if (currentSegment.length > 1) {
        segments.push(currentSegment);
    }

    return segments;
}

const map = L.map('map', {
    center: [0, 0],
    zoom: 3,
    scrollWheelZoom: false
});

L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.opentopomap.org/">OpenTopoMap</a> contributors'
}).addTo(map);

const issIcon = L.icon({
    iconUrl: '/static/iss/images/iss-png.png',
    iconSize: [50, 50],
    iconAnchor: [25, 25]
});

let marker = null;
let footprintCircle = null;
let animationTimeout = null;
const visibilityRadius = 648000;

async function loadISSPath() {
    try {
        const response = await fetch("/iss/orbit/");
        const data = await response.json();
        const pathSegments = splitPathAtDateLine(data.path);

        map.eachLayer(layer => {
            if (layer instanceof L.Polyline) {
                map.removeLayer(layer);
            }
        });

        pathSegments.forEach(segment => {
            if (segment.length > 1) {
                const polyline = L.polyline(segment, { 
                    color: "red", 
                    weight: 3,
                    opacity: 0.8 
                }).addTo(map);
                polyline.bringToBack();
            }
        });

        const currentPos = pathSegments[0][0];
        map.setView(currentPos, 3);

        if (!marker) {
            marker = L.marker(currentPos, { icon: issIcon }).addTo(map);
        } else {
            marker.setLatLng(currentPos);
        }

        if (!footprintCircle) {
            footprintCircle = L.circle(currentPos, {
                color: 'rgba(255, 0, 0, 0.5)',
                fillColor: 'rgba(255, 0, 0, 0.33)',
                fillOpacity: 0.2,
                radius: visibilityRadius
            }).addTo(map);
        } else {
            footprintCircle.setLatLng(currentPos);
        }

        if (animationTimeout) {
            clearTimeout(animationTimeout);
        }

        const flatPath = pathSegments.flat();

        setTimeout(() => {
            animateISS(flatPath, 0);
        }, 500);

    } catch (err) {
        console.error("ERROR: failed to load the ISS position:", err);
    }
}

function animateISS(path, currentIndex = 0) {
    if (currentIndex >= path.length) return;

    const [lat, lon] = path[currentIndex];

    if (marker && typeof marker.setLatLng === 'function') {
        marker.setLatLng([lat, lon]);
    }

    if (footprintCircle && typeof footprintCircle.setLatLng === 'function') {
        footprintCircle.setLatLng([lat, lon]);
    }

    animationTimeout = setTimeout(() => {
        animateISS(path, currentIndex + 1);
    }, 10000);
}

loadISSPath();
