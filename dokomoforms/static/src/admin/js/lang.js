
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

        if (lang_obj[selected_lang]) {
            return lang_obj[selected_lang];
        } else if(default_lang && lang_obj[default_lang]) {
            // if a default lang is specified, fall back that
            return lang_obj[default_lang];
        }
        // finally, fall back to first available language
        return lang_obj[_.keys(lang_obj)[0]];
    }

    function setSelectedLanguage(lang) {
        selected_lang = lang;
    }

    parseTranslateable.setSelectedLanguage = setSelectedLanguage;
    parseTranslateable.getAvailableLanguages = getAvailableLanguages;

    return parseTranslateable;

})();
