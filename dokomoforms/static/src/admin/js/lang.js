
var _ = require('lodash');

module.exports = (function() {
    var selected_lang = window.CURRENT_USER_PREFS ? window.CURRENT_USER_PREFS.default_language : 'English';

    function getAvailableLanguages(lang_obj) {
        if (!_.isPlainObject(lang_obj)) {
            throw new Error('lang_obj must be a plain object with keys indicating language');
        }
        return _.keys(lang_obj);
    }

    function parseTranslateable(lang_obj, default_lang) {
        if (!_.isPlainObject(lang_obj)) {
            throw new Error('lang_obj must be a plain object with keys indicating language');
        }

        return lang_obj[selected_lang || default_lang];
    }

    function setSelectedLanguage(lang) {
        selected_lang = lang;
    }

    parseTranslateable.setSelectedLanguage = setSelectedLanguage;
    parseTranslateable.getAvailableLanguages = getAvailableLanguages;

    return parseTranslateable;

})();
