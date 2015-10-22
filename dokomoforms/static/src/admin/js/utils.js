// A place for common utility functions

var $ = require('jquery');

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

    return {
        initTooltips: _initTooltips,
        initPopovers: _initPopovers
    };
})();
