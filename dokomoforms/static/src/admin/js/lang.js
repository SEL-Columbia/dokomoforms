
var _ = require('lodash');

module.exports = (function() {
    var default_lang = window.CURRENT_USER_PREFS ? window.CURRENT_USER_PREFS.default_language : 'English',
        selected_lang = 'English';

    function getAvailableLanguages(lang_obj) {
        if (!_.isPlainObject(lang_obj)) {
            throw new Error('lang_obj must be a plain object with keys indicating language');
        }
        return _.keys(lang_obj);
    }

    function parseTranslateable(lang_obj) {
        if (lang_obj[selected_lang]) {
            return lang_obj[selected_lang];
        } else if(lang_obj[default_lang]) {
            return lang_obj[default_lang];
        }
    }

    function setSelectedLanguage(lang) {
        selected_lang = lang;
    }

    function setDefaultLanguage(lang) {
        default_lang = lang;
    }

    parseTranslateable.setSelectedLanguage = setSelectedLanguage;
    parseTranslateable.setDefaultLanguage = setDefaultLanguage;
    parseTranslateable.getAvailableLanguages = getAvailableLanguages;

    return parseTranslateable;

})();
