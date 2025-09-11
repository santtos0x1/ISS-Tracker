const map = L.map('map').setView([0, 0], 2);
const map_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'; 
const icon_path = '/static/images/iss-map-icon.png';

L.tileLayer(map_url, {
    attribution: 'Tiles © Esri'
}).addTo(map);

const issIcon = L.icon({
    iconUrl: icon_path,
    iconSize: [35, 35],
    iconAnchor: [25, 25]
});

const marker = L.marker([0, 0], { icon: issIcon }).addTo(map);
let issPath = [];
let polyline = L.polyline(issPath, { color: 'green' }).addTo(map);

async function updateISS() {
    try {
        const url_api = 'http://api.open-notify.org/iss-now.json';
        const response = await fetch(url_api);
        const data = await response.json();
        const lat = parseFloat(data.iss_position.latitude);
        const lon = parseFloat(data.iss_position.longitude);

        marker.setLatLng([lat, lon]);
        map.setView([lat, lon], map.getZoom());
        map.panTo([lat, lon]);
        issPath.push([lat, lon]);

        if (issPath.length > 50) {
            issPath.shift(); 
        }

        polyline.setLatLngs(issPath);
        
    } catch (err) {
        console.error('Error to search the ISS position:', err);
    }
}

updateISS();
setInterval(updateISS, 5000);