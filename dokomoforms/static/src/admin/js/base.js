var $ = require('jquery'),
    cookies = require('../../common/js/cookies'),
    ps = require('../../common/js/pubsub'),
    SettingsModal = require('./modals/settings-modal'),
    Notification = require('./notification'),
    utils = require('./utils');

module.exports = (function() {

    function init() {
        utils.initTooltips();
        utils.initPopovers();
        _globalAjaxSetup();
        _setupGlobalEventHandlers();

    }

    /**
     * Attach CSRF token header to all requests.
     */
    function _globalAjaxSetup() {
        $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
            var _xsrf = cookies.getCookie('_xsrf');
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
