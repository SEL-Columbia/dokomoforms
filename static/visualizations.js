function drawLineGraph(time_data) {
}

function drawBarGraph(bar_data) {
}
 
function drawMap(map_data) {

    var map = L.map('vis_map', {
        dragging: true,
        zoom: 14,
        zoomControl: false,
        doubleClickZoom: false,
        attributionControl: false
    });

    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);

    var sw_lat = parseFloat(map_data[0][1]);
    var sw_lng = parseFloat(map_data[0][0]);
    var ne_lat = parseFloat(map_data[0][1]);
    var ne_lng = parseFloat(map_data[0][0]);

    for (i = 0; i < map_data.length; i++) {
        var location = map_data[i];
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
        marker.options.icon = new L.icon({iconUrl: "/static/img/icons/selected-point.png", iconAnchor: [15, 48]});

        var answers = JSON.parse(map_data[i][2]).answers;
        var submission_text = "<ul>";
        for(j=0; j < answers.length; j++){
            var ans = answers[j];
            submission_text += "<li><strong>" + ans.sequence_number + ". " + ans.question_title + "</strong><br />" + ans.answer +"</li>";
        }
        submission_text += "</ul";

        marker.bindPopup(submission_text);

        marker.addTo(map);
    }

    map.fitBounds([[sw_lat, sw_lng],
                   [ne_lat, ne_lng]]);
}
