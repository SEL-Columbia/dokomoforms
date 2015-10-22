// A place for common utility functions

var $ = require('jquery'),
    _ = require('lodash'),
    moment = require('moment');

module.exports = (function() {
    /**
     * Enable tooltips within the element defined by selector
     * @param  {String} selector [description]
     */
    function _initTooltips(selector) {
        selector = selector || 'body';
        $('[data-toggle="tooltip"]').tooltip({
            container: selector
        });
    }

    /**
     * Enable popover within the element defined by selector
     * @param  {String} selector [description]
     */
    function _initPopovers(selector) {
        selector = selector || 'body';
        $('[data-toggle="popover"]').popover({
            container: selector
        });
    }

    /**
     * Populate an element with a formated date.
     * @param  {String} selector   A CSS selector whose corresponding element will be filled with the formatted date
     * @param  {String} dateString The input datetime string
     * @param  {String} format     The desired output format (moment.js)
     * @return {String}            The formatted date string
     */
    function _populateDate(selector, dateString, format) {
        format = format || 'MMM D, YYYY';
        var formatted = dateString;
        if (moment(dateString).isValid()) {
            formatted = moment(dateString).format(format);
        }
        $(selector).text(formatted);
    }

    /**
     * Given a dictionary of selector keys with datetime string values and
     * an optional format, populate the selected elements with a formatted
     * datetime string
     * @param  {Object} datetimes An object of css selector keys with datetime string values
     * @return {String}           An optional moment.js format string
     */
    function _populateDates(datetimes, format) {
        // window.DATETIMES is a dictionary with selectors as keys and
        // datetime strings as values.
        if (datetimes) {
            _.forEach(datetimes, function(datetime, selector) {
                _populateDate(selector, datetime, format);
            });
        }
    }

    return {
        initTooltips: _initTooltips,
        initPopovers: _initPopovers,
        populateDates: _populateDates,
        populateDate: _populateDate
    };

})();
