(function() {


var App = {
    questions: [
        {
            name: 'facility_name',
            label: 'Health facility name',
            type: 'text'
        },
        {
            name: 'facility_location',
            label: 'Facility location',
            type: 'location'
        },
        {
            name: 'bed_capacity',
            label: 'Bed Capacity?',
            type: 'integer',
            min: 0
        },
        {
            name: 'suspected_cases',
            label: 'Number of suspected Ebola cases',
            type: 'integer',
            min: 0
        },
        {
            name: 'confirmed_cases',
            label: 'Number of confirmed Ebola cases',
            type: 'integer',
            min: 0
        },
        {
            name: 'confirmed_deaths',
            label: 'Number of confirmed Ebola deaths',
            type: 'integer',
            min: 0
        },
        {
            name: 'recovered_cases',
            label: 'Number of recovered and released Ebola cases',
            type: 'integer',
            min: 0
        },
        {
            name: 'litres_bleach',
            label: 'Liters of bleach',
            type: 'integer',
            min: 0
        },
        {
            name: 'num_gloves',
            label: 'Number of gloves',
            type: 'integer',
            min: 0
        },
        {
            name: 'face_shields',
            label: 'Number of face shields',
            type: 'integer',
            min: 0
        },
        {
            name: 'num_respirators',
            label: 'Number of N95 respirators',
            type: 'integer',
            min: 0
        },
        {
            name: 'num_goggles',
            label: 'Number of goggles',
            type: 'integer',
            min: 0
        }
    ]
};


var Widgets = {};
Widgets.text = {
    render: function(data) {
        return '<input type="text">'
    },
    events: function(data, page) {
        
    },
    getData: function(data, page) {
        
    }
}

Widgets.location = {
    render: function(data) {
        var value = data.value || '';
        return '<input type="text">';
    },
    events: function(data) {
        function findLocation() {
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    var coords = position.coords;
                    alert(coords.latitude + ', ' + coords.longitude);
                }, function error() {
                    alert('error')
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        }
    }
};





$('.page_nav__prev, .page_nav__next').click(function() {
    var active = $('.pages--active');
    if (this.classList.contains('page_nav__prev')) {
        var switched = active.prev('.pages__page')
            .addClass('pages--active');
    } else {
        var switched = active.next('.pages__page')
            .addClass('pages--active');
    }
    if (switched.length) {
        active.removeClass('pages--active');
        updateProgress();
    }
    return false;
});


function updateProgress() {
    var active = $('.pages--active');
    var total = $('.pages__page').length;
    var completed = active.prevAll('.pages__page').length + 1;
    $('.page_nav__progress').text(completed + ' / ' + total);
}


    
})();