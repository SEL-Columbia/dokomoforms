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

    return {
        initTooltips: _initTooltips
    };
})();
