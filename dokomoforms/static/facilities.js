//TODO:Remove reference to App

/*
 * Revisit get facilities API call. 
 *
 * @lat: latitude value
 * @lng: longitude value
 * @rad: radius in KM
 * @lim: number of facilities to return
 * @cb: Success callback
 */
function getNearbyFacilities(lat, lng, rad, lim, cb) {
    var url = "http://staging.revisit.global/api/v0/facilities.json"; 

    // Revisit ajax req
    $.get(url,{
            near: lat + "," + lng,
            rad: rad,
            limit: lim,
            //sortDesc: "updatedAt",
            fields: "name,uuid,coordinates,properties:sector", //filters results to include just those three fields,
        },
        function(data) {
            facilities = {};
            data.facilities.forEach(function(facility) {
                facilities[facility.uuid] = facility;
            });
            // Add in our unsynced ones as well
            Object.keys(App.unsynced_facilities).forEach(function(uuid) {
                facilities[uuid] = App.unsynced_facilities[uuid];
            });

            App.facilities = facilities;
            localStorage.setItem("facilities", JSON.stringify(facilities));
            if (cb) {
                cb(facilities); //drawFacillities callback probs
            }
        }
    );
}

/*
 * Revisit post facility API call. 
 *
 * @facility: facility object to post
 */
function postNewFacility(facility) {
    var url = "http://staging.revisit.global/api/v0/facilities.json"; 

    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(facility),
        processData: false,
        dataType: 'json',
        success: function() {
            //App.message('Facility Added!', 'message-primary');
            // If posted, we don't an unsynced reference to it anymore
            delete App.unsynced_facilities[facility.uuid];
        },
        
        headers: {
            "Authorization": "Basic " + btoa("dokomoforms" + ":" + "password")
                //DONT DO THIS XXX XXX
        },

        error: function() {
            //App.message('Facility submission failed, will try again later.', 'message-warning');
        },
        
        complete: function() {
            localStorage.setItem("facilities", 
                    JSON.stringify(App.facilities));

            localStorage.setItem("unsynced_facilities", 
                    JSON.stringify(App.unsynced_facilities));

        }
    });
}

/*
 * Generate objectID compatitable with Mongo for the Revisit API
 *
 * Returns an objectID string
 */
function objectID() {
    return 'xxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[x]/g, function() {
        var r = Math.random()*16|0;
        return r.toString(16);
    });
}

exports.getNearbyFacilities = getNearbyFacilities; 
exports.postNewFacility = postNewFacility;
exports.objectID = objectID;

