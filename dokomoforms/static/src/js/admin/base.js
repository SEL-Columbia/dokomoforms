var $ = require('jquery'),
    submissionModals = require('./submission-modal'),
    persona = require('../common/persona');

module.exports = (function() {

    /**
     * [initTooltips description]
     * @return {[type]} [description]
     */
    function initTooltips() {
        // enable tooltips
        $('[data-toggle="tooltip"]').tooltip({
            container: 'body'
        });
    }


    function init() {
        initTooltips();

        // setup handlers for submission modals
        submissionModals.init();

        // setup handlers for persona events
        persona.init();
    }

    return {
        init: init
    };

})();
