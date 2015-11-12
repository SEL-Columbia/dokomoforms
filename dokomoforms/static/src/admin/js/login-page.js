var persona = require('../../common/js/persona');

var LoginPage = (function() {

    function init() {
        persona.init();
    }

    return {
        init: init
    };
})();

LoginPage.init();
