(function() {

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

findLocation();

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