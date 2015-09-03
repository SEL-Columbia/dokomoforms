var React = require('react'),
    Application = require('./Application'),
    config = require('./conf/config');

/*
 * Entry point for template
 *
 * @survey: JSON representation of the survey
 * @revisit_url: Revisit url, set globally
 */
window.init = function(survey, url) {
    console.log('init');
    // Set revisit url
    config.revisit_url = url;

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