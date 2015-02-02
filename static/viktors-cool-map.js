function displayViktorPoints(coordinates) {
    var map = L.map('viktormap', {
        center: [40.8138912, -73.9624327],
        dragging: true,
        zoom: 14,
        zoomControl: false,
        doubleClickZoom: false,
        attributionControl: false
    });

    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);

    for (i = 0; i < coordinates.length; i++) {
        var location = coordinates[i];
        var lng = parseFloat(location[0]);
        var lat = parseFloat(location[1]);
        // stored lon/lat in revisit, switch around
        var marker = new L.marker([lat, lng], {
            riseOnHover: true
        });
        marker.options.icon = new L.icon({iconUrl: "/static/img/icons/normal_water.png"});
        marker.addTo(map);
    }
}
