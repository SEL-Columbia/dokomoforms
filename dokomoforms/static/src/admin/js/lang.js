
var _ = require('lodash');

module.exports = (function() {
    var preferred_lang = window.CURRENT_USER_PREFS ? window.CURRENT_USER_PREFS.default_language : 'English';

    function getAvailableLanguages(lang_obj) {
        if (!_.isPlainObject(lang_obj)) {
            throw new Error('lang_obj must be a plain object with keys indicating language');
        }
        return _.keys(lang_obj);
    }

    function parseTranslateable(lang_obj, survey) {
        console.log('translating: ', lang_obj, survey);
        if (!_.isPlainObject(lang_obj)) {
            throw new Error('lang_obj must be a plain object with keys indicating language');
        }

        // first check for survey-specific lang pref
        var prefs = window.CURRENT_USER_PREFS;
        if (prefs[survey.id] && prefs[survey.id]['display_language']) {
            return lang_obj[prefs[survey.id]['display_language']];
        }

        // if no survey-specific lang, try user's preferred default language
        if (lang_obj[preferred_lang]) {
            return lang_obj[preferred_lang];
        }

        // finally, fall back to survey's default lang
        return lang_obj[survey.default_language];
    }

    function setSelectedLanguage(lang) {
        preferred_lang = lang;
    }

    parseTranslateable.setSelectedLanguage = setSelectedLanguage;
    parseTranslateable.getAvailableLanguages = getAvailableLanguages;

    return parseTranslateable;

})();
