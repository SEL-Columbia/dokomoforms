var $ = require('jquery'),
    cookies = require('../../common/js/cookies'),
    ps = require('./pubsub'),
    submissionModals = require('./submission-modal'),
    SettingsModal = require('./modals/settings-modal'),
    Notification = require('./notification'),
    persona = require('../../common/js/persona'),
    utils = require('./utils');

module.exports = (function() {

    function init() {
        utils.initTooltips();
        _globalAjaxSetup();
        _setupGlobalEventHandlers();

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

    function _setupGlobalEventHandlers() {
        $(document).on('click', '.nav-settings', function() {
            new SettingsModal(window.CURRENT_USER_ID);
        });

        ps.subscribe('settings:saved', function() {
            new Notification('Settings saved.', 'success');
        });

        ps.subscribe('settings:save-error', function() {
            new Notification('Whoops! There was a problem saving settings.', 'danger');
        });
    }

    return {
        init: init
    };

})();
