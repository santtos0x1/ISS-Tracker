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
                currentSegment.push([prevLat, prevLon]);

                if (currentSegment.length > 1) {
                    segments.push([...currentSegment]);
                }

                currentSegment = [[lat, lon]];

            } else {
                currentSegment.push([lat, lon]);
            }

        } else {
            currentSegment.push([lat, lon]);
        }
    }
    
    if (currentSegment.length > 1) {
        segments.push(currentSegment);
    }

    return segments;
}

const map = L.map('map').setView([0, 0], 2);
const map_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'; 

L.tileLayer(map_url, {
    attribution: 'Tiles © Esri'
}).addTo(map);

const issIcon = L.icon({
    iconUrl: '/static/iss/images/iss-map-icon.png',
    iconSize: [35, 35],
    iconAnchor: [25, 25]
});

let marker = null;
let animationTimeout = null;

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
        
        pathSegments.forEach((segment, index) => {
            if (segment.length > 1) {
                const polyline = L.polyline(segment, { 
                    color: "yellow", 
                    weight: 3,
                    opacity: 0.8 
                }).addTo(map);

                polyline.bringToBack();
            }
        });

        const normalizedPath = data.path.map(([lat, lon]) => {
            if (lon > 180) lon -= 360;
            if (lon < -180) lon += 360;

            return [lat, lon];
        });

        if (normalizedPath.length > 0) {
            map.setView(normalizedPath[0], 3);

            if (!marker) {
                marker = L.marker(normalizedPath[0], { icon: issIcon }).addTo(map);
                console.log("Marcador criado na posição:", normalizedPath[0]);
            } else {
                marker.setLatLng(normalizedPath[0]);
                console.log("Marcador movido para:", normalizedPath[0]);
            }

            if (animationTimeout) {
                clearTimeout(animationTimeout);
            }
            
            setTimeout(() => {
                animateISS(normalizedPath, 0);
            }, 500);
        }
    } catch (err) {
        console.error("ERROR: failed to load the ISS position:", err);
    }
}

function animateISS(path, currentIndex = 0) {
    const [lat, lon] = path[currentIndex];

    if (marker && typeof marker.setLatLng === 'function') {
        marker.setLatLng([lat, lon]);
    } else {
        console.error("The marker does not have setLatLng:", marker);
    }

    animationTimeout = setTimeout(() => {
        animateISS(path, currentIndex + 1);
    }, 10000);
}

loadISSPath();