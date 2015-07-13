var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

var getNearbyFacilities = require('./facilities.js').getNearbyFacilities;
var postNewFacility = require('./facilities.js').postNewFacility;
var Widgets = require('./widgets.js').Widgets;
var Survey = require('./survey.js').Survey;

// In memory variables used across the webapp
var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    location: {},
    submitter_name: '',
    submitter_email: '',
    survey: null,
};

/*
 * Initilize the webapp by creating a new survey, and reading any values saved 
 * in storage. Function is called on page load.
 *
 * @survey: JSON representation of the survey
 */
App.init = function(survey) {
    var self = this;

    var answers = JSON.parse(localStorage[survey.id] || '{}');
    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name || "";
    self.submitter_email = localStorage.email || "";
    
    console.log(survey.nodes);
    self.survey = new Survey(survey.id, 
            survey.version, 
            survey.nodes, 
            answers,
            survey.metadata, 
            survey.title[survey.default_language], 
            survey.created_on,
            survey.last_update_time,
            survey.default_language
            );

    // Set up an empty dictonary if no unsynced surveys are found
    if (!localStorage.unsynced) {
        localStorage.unsynced = JSON.stringify({});
    }

    // Load up any unsynced submissions
    App.unsynced = JSON.parse(localStorage.unsynced)[self.survey.id] || []; 
    // Set up survey location
    App.location = answers['location'] 
        || survey.metadata.location 
        //|| {'lat': 40.8138912, 'lon': -73.9624327};
        || {};


    // Load up any unsynced facilities
    App.unsynced_facilities = 
        JSON.parse(localStorage.unsynced_facilities || "{}");

    // Load any facilities
    App.facilities = JSON.parse(localStorage.facilities || "{}");
    if (JSON.stringify(App.facilities) === "{}" && navigator.onLine) {
        // See if you can get some new facilities
        getNearbyFacilities(App.location.lat, App.location.lng, 
            FAC_RAD, // Radius in km 
            NUM_FAC, // limit
            null// what to do with facilities 
        );
    }

    // Listen to appcache updates, reload JS.
    window.applicationCache.addEventListener('updateready', function() {
        console.log('app updated, reloading...');
        window.location.reload();
    });

    // Clicking burger
    $('header')
        .on('click', '.menu', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();
        });

    // Clear all survey data
    $('header')
        .on('click', '.menu_clear', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            localStorage.clear();
            App.splash();
            window.location.reload();
            App.message('All survey data erased.', 'Surveys Nuked', 'message-warning');
        });

    // Clear active survey data
    $('header')
        .on('click', '.menu_restart', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            App.clearState();
            App.splash();
            window.location.reload();
            App.message('Active survey has been cleared.', 'Survey Reset', 'message-warning');
        });

    // Save active survey state
    $('header')
        .on('click', '.menu_save', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            App.saveState();
            App.message('Active survey has been saved.', 'Survey Saved', 'message-success');
        });
        
    // Begin survey at Application splash page
    App.splash();
};

/*
 * Submit all unsynced surveys to Dokomoforms. Should only be called on when 
 * device has a web connection. Calls App.submit
 *
 * Removes successfully submitted survey from unsynced array and localStorage. 
 * Launches modal on completion.
 */
App.sync = function() {
    var self = this;
    //$('.submit_modal')[0].click(); // Pop Up Submitting Modal
    self.countdown = App.unsynced.length; //JS is single threaded no race condition counter
    self.count = App.unsynced.length; //JS is single threaded no race condition counter
    var endSync = function() {
        //$('.submit_modal')[0].click(); // Remove submitting modal;
        App.splash();
        if (!App.unsynced.length) {
            App.message('All ' + self.count + ' surveys synced succesfully.', 
                    'Survey Synced', 'message-success');
        } else {
            App.message(App.unsynced.length + ' survey(s) failed to sync succesfully. Please try again later.', 
                    'Survey Sync Failed', 'message-error');
        }
    };
    _.each(App.unsynced, function(survey) {
        App.submit(survey, 
            function(survey) { 
                console.log('done');
                // Has to be there
                var idx = App.unsynced.indexOf(survey);
                App.unsynced.splice(idx, 1);
                var unsynced = JSON.parse(localStorage.unsynced); 
                unsynced[self.survey.id] = App.unsynced;
                localStorage['unsynced'] = JSON.stringify(unsynced);
                --self.countdown; 
                
                if (self.countdown === 0) {  
                    endSync();
                }
            },

            function(err, survey) { 
                console.log('fail');
                window.err = err;
                --self.countdown; 

                if (self.countdown === 0) {
                    endSync();
                }
            } 
        );
    });

    // Attempt to submit unsynced facilities to Revisit
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });
};

/*
 * Trigger modal event, powered by ratchet. 
 *
 * @text: modal message
 * @title: modal title
 * @style: modal type (possible classes in css)
 */
App.message = function(text, title, style) {
    $('.message_btn')[0].click();
    
    $('.modal_header').empty()
        // Remove any posible class attached to modal div
        .removeClass('message-primary')
        .removeClass('message-error')
        .removeClass('message-warning')
        .removeClass('message-success')
        // Attach requested class
        .addClass(style)
        .text(title);

    // Message text region
    $('.message')
        .text(text);
};

/* 
 * Webapp splash page, text loaded from template.
 * This is where user syncs and starts surveys.
 */ 
App.splash = function() {
    $('header').removeClass('title-extended');
    $('.title_menu').hide();
    var self = this;
    var survey = self.survey;
    $('.overlay').hide(); // Always remove overlay after moving.

    // Update page nav and footer
    var barnav  = $('.bar-nav');
    var barnavHTML = $('#template_nav__splash').html();
    var barnavTemplate = _.template(barnavHTML);
    var compiledHTML = barnavTemplate({
        'org': survey.org,
    });
    
    barnav.empty()
        .html(compiledHTML);

    var barfoot = $('.bar-footer');
    barfoot.removeClass('bar-footer-extended');
    barfoot.removeClass('bar-footer-super-extended');
    barfoot.css("height", "");

    var barfootHTML = $('#template_footer__splash').html();
    var barfootTemplate = _.template(barfootHTML);
    compiledHTML = barfootTemplate({
    });

    barfoot.empty()
        .html(compiledHTML)
        .find('.start_btn')
        .one('click', function() {
            // Render first question
            App.survey.render(App.survey.first_question);
        });


    // Set up content
    var content = $('.content');
    content.removeClass('content-shrunk');
    content.removeClass('content-super-shrunk');

    var splashHTML = $('#template_splash').html();
    var splashTemplate = _.template(splashHTML);
    compiledHTML = splashTemplate({
        'survey': survey,
        'online': navigator.onLine,
        'name': App.submitter_name,
        'unsynced': App.unsynced,
        'unsynced_facilities': App.unsynced_facilities
    });

    content.empty()
        .data('index', 0)
        .html(compiledHTML)
        .find('.sync_btn')
        .one('click', function() {
            if (navigator.onLine) {
                App.sync();
            } else {
                App.message('Please connect to the internet first.', 'Connection Error', 'message-warning');
            }
        });
};

/*
 * Submits a single survey to Dokomoforms.
 *
 * @survey: Object representation of a completed survey
 * @done: Successful submission callback
 * @fail: Failed submission callback
 */
App.submit = function(survey, done, fail) {
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    
    // Update submit time
    survey.submission_time = new Date().toISOString();

    $.ajax({
        url: '/api/v0/surveys/'+survey.survey_id+'/submit',
        type: 'POST',
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(survey),
        headers: {
            "X-XSRFToken": getCookie("_xsrf")
        },
        dataType: 'json',
        success: function() {
            done(survey);
        },
        error: function(err, anything) {
            console.log(anything);
            fail(err, survey);
        }
    });

    console.log('synced submission:', survey);
    console.log('survey', '/api/v0/surveys/'+survey.survey_id+'/submit');
}

/*
 * Save the current state of the survey (i.e question answers) to localStorage.
 */
App.saveState = function() {

    // Save answers in storage
    var answers = this.survey.getState();
    localStorage[this.survey.id] = JSON.stringify(answers);
};

/*
 * Clear the current state of the survey (i.e question answers) and remove the 
 * state in localStorage.
 */
App.clearState = function() {

    // Reset location
    App.location = {};

    // Clear answers locally
    this.survey.clearState();

    // Clear answers in localStorage
    localStorage[this.survey.id] = JSON.stringify({});
}

// For requiring
exports = exports || {};
exports.App = App;

// For window
window = window || {};
window.App = App;
