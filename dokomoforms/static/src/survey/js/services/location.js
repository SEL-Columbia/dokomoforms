/**
 * A light wrapper on the browser's location service.
 */
module.exports = (function() {
    var latestPosition = null;

    /**
     * Return the last fetched position, or null
     * @return {Position} The position object.
     */
    function _getLastKnownPosition() {
        return latestPosition;
    }

    /**
     * Fetch the current position using geolocation.
     *
     * Stores the last saved position in latestPosition, retievable by getLastKnownPosition.
     *
     * @param  {Function} success_cb A success callback
     * @param  {Fucntion} fail_cb    A fail callback
     */
    function _fetchPosition(success_cb, fail_cb) {
        console.log('_fetchPosition');
        var ts = Date.now();
        // reset latestPosition
        latestPosition = null;

        // try to fetch a new current position using GPS
        navigator.geolocation.getCurrentPosition(

            function success(position) {
                console.log('Position fetched in ' + (Date.now() - ts) + ' milliseconds.');
                latestPosition = position;
                if (success_cb) {
                    success_cb(position);
                }
            },

            function error(err) {
                console.log('Location could not be fetched.', err);
                if (fail_cb) {
                    fail_cb(err);
                }
            },

            {
                enableHighAccuracy: true
                // timeout: 20000,
                // maximumAge: 0
            }
        );
    }

    return {
        fetchPosition: _fetchPosition,
        getLastKnownPosition: _getLastKnownPosition
    };
})();
