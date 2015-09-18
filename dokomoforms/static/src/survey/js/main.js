var React = require('react'),
    Application = require('./Application'),
    config = require('./conf/config'),
    utils = require('./services/utils'),
    locationService = require('./services/location');

/*
 * Entry point for template
 *
 * @survey: JSON representation of the survey
 * @revisit_url: Revisit url, set globally
 */
window.init = function(survey, url) {
    console.log('init', survey);
    // Set revisit url
    config.revisit_url = url;

    // check if the survey has a location question, if so start GPS now...
    if (utils.surveyHasQuestionType(survey, 'location') || utils.surveyHasQuestionType(survey, 'facility')) {
        locationService.fetchPosition();
    }

    // Listen to appcache updates, reload JS.
    window.applicationCache.addEventListener('updateready', function() {
        alert('Application updated, reloading ...');
        window.applicationCache.swapCache();
        window.location.reload();
    });

    React.render(
            <Application survey={survey} />,
            document.body
    );
};
