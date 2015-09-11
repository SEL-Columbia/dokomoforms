var $ = require('jquery'),
    cookies = require('../../common/js/cookies'),
    submissionModals = require('./submission-modal'),
    persona = require('../../common/js/persona'),
    utils = require('./utils'),
    _t = require('./lang');

module.exports = (function() {

    function init() {
        utils.initTooltips();
        _globalAjaxSetup();

        // setup handlers for submission modals
        // TODO: refactor submission modals to a proper module.
        submissionModals.init();

        // setup handlers for persona events
        persona.init();
    }

    /**
     * Attach CSRF token header to all requests.
     */
    function _globalAjaxSetup() {
        $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
            var _xsrf = cookies.getCookie('_xsrf');
            console.log(_xsrf);
            jqXHR.setRequestHeader('X-XSRFToken', _xsrf);
        });
    }

    return {
        init: init
    };

})();
