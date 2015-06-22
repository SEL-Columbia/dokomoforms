var map = L.map('map', {
    dragging: true,
    zoom: 2,
    center: [0, 0],
    zoomControl: false,
    doubleClickZoom: false,
    attributionControl: false
});

L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);


function drawBox(en, ws, colour, obj) {
    // define rectangle geographical bounds
     var bounds = [[en[1], ws[0]], [ws[1], en[0]]];
    
     if (!obj) {
        L.rectangle(bounds, {color: colour, weight: 2, fill: false}).addTo(map);
     } else {
        var count = Math.floor(((obj.count)/1000 * 4095))
        var col = "#" + count.toString(16);
        var rec = L.rectangle(bounds, {color: colour, fillColor: col, weight: 2, fill: true});
        rec
            .bindPopup(
                    "<p>obj compressed: " + obj.compressedSize / 1000000 + "MB</p>"
                    + "<p>obj uncompressed: "  + obj.uncompressedSize / 1000000 + "MB</p>"
                    + "<p>obj count: " + obj.count + "</p>"
                    + "<p>obj center: " + obj.center + "</p>");
                    
        rec.addTo(map)
        

     }

};

function updateStats(tree, bounds) {
    console.log("Updating Stats");
    var stats = document.getElementById("stats");
    var ny = [];
    tree.getNNearestFacilities(7.353078, 5.118915, 100, 5).forEach(function(site) {
        ny.push({
            'coordinates': site.coordinates,
            'name': site.name
        });
    });

    var ng = [];
    tree.getNNearestFacilities(40.80690, -73.96536, 100, 5).forEach(function(site) {
        ng.push({
            'coordinates': site.coordinates,
            'name': site.name
        });
    });

    L.rectangle(bounds, {color: "#FFA500", weight: 2, fill: false}).addTo(map);

    stats.innerHTML = 
        "<p> Query for region within: " + bounds + "</p>"
        + "<p> Compressed Size: "+tree.getCompressedSize() / 1000000+"</p>"
        + "<p> Uncompressed Size: "+tree.getUncompressedSize() / 1000000+"</p>"
        + "<p> Facilities count: "+tree.getCount() +"</p>"
        + "<p> Tree count: "+tree.getLeaves().length+"</p>"
        + "<p> 5 in a 100km radius nearest facilities in nigeria near 7.353, 5.118  "
        + JSON.stringify(ny)+"</p>"
        + "<p> 5 in a 100km radius nearest facilities in nyc near 40.806 -73.965  "
        + JSON.stringify(ng)+"</p>"
        + "<p> Percentage of original size: "+ tree.getCompressedSize()/tree.getUncompressedSize() * 100+"</p>";
}

