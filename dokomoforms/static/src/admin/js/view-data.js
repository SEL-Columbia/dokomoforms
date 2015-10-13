var $ = require('jquery'),
    _ = require('lodash'),
    L = require('leaflet'),
    base = require('./base'),
    sub_modals = require('./submission-modal');

var ViewData = (function() {
    var maps = {},
        map_data = {};

    function init(_map_data) {
        base.init();
        // TODO: is this check necessary?
        if (window.CURRENT_USER_ID !== 'None') {
            map_data = _map_data;
            setupEventHandlers();
        }
    }

    function setupEventHandlers() {
        $(document).on('click', '.question-title-bar', function() {
            var $el = $(this),
                id = $el.attr('rel');

            if ($el.hasClass('open')) {
                $el.removeClass('open');
            } else {
                $el.addClass('open');
            }

            $el.siblings('.question-stats').slideToggle();

            if ($el.hasClass('question-type-location') || $el.hasClass('question-type-facility')) {
                if (!maps[id]) {
                    console.log(id);
                    drawMap(id, map_data[id]);
                }
            }
        });
    }

    function drawMap(element_id, map_data) {
        var markers = [];

        var map = L.map(element_id, {
            dragging: true,
            zoom: 14,
            // zoomControl: false,
            // doubleClickZoom: false,
            attributionControl: false
        });

        maps[element_id] = map;

        markers = [];

        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);

        _.each(map_data.map_data, function(answer) {
            var coordinates = answer.coordinates,
                marker = new L.marker([coordinates.lat, coordinates.lng], {
                    riseOnHover: true
                });
            marker.options.icon = new L.icon({
                iconUrl: '/static/dist/admin/img/icons/normal_base.png',
                iconAnchor: [13, 30]
            });
            marker.on('click', function() {
                sub_modals.openSubmissionDetailModal(answer.submission_id);
            });
            markers.push(marker);
        });

        if (markers.length) {
            var markers_group = new L.featureGroup(markers);
            markers_group.addTo(map);
            map.fitBounds(markers_group.getBounds(), {
                padding: [40, 40]
            });
        } else {
            console.log('No submissions include location.');
        }
    }

    return {
        init: init
    };
})();

// expose this module globally so that we can bootstrap it
window.ViewData = ViewData;
