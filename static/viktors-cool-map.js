function displayViktorPoints(coordinates) {
    var map = L.map('viktormap', {
        //center: [40.8138912, -73.9624327],
        dragging: true,
        zoom: 14,
        zoomControl: false,
        doubleClickZoom: false,
        attributionControl: false
    });

    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);

    var sw_lat = parseFloat(coordinates[0][1]);
    var sw_lng = parseFloat(coordinates[0][0]);
    var ne_lat = parseFloat(coordinates[0][1]);
    var ne_lng = parseFloat(coordinates[0][0]);

    for (i = 0; i < coordinates.length; i++) {
        var location = coordinates[i];
        var lng = parseFloat(location[0]);
        if (lng < sw_lng) {
            sw_lng = lng;
        } else if (lng > ne_lng) {
            ne_lng = lng;
        }
        var lat = parseFloat(location[1]);
        if (lat < sw_lat) {
            sw_lat = lat;
        } else if (lat > ne_lat) {
            ne_lat = lat;
        }
        // stored lon/lat in revisit, switch around
        var marker = new L.marker([lat, lng], {
            riseOnHover: true
        });
        marker.options.icon = new L.icon({iconUrl: "/static/img/icons/normal_water.png"});
        marker.addTo(map);
    }

    map.fitBounds([[sw_lat, sw_lng],
                   [ne_lat, ne_lng]]);
}
