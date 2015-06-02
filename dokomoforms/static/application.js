var NEXT = 1;
var PREV = -1;
var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

var getNearbyFacilities = require('./facilities.js').getNearbyFacilities;
var postNewFacility = require('./facilities.js').postNewFacility;
var Widgets = require('./widgets.js');
var Survey = require('./survey.js');

var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    location: {},
    submitter_name: ''
};

App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, 
            survey.survey_version, 
            survey.questions, 
            survey.survey_metadata, 
            survey.survey_title, 
            survey.created_on,
            survey.last_updated);

    var start_loc = survey.survey_metadata.location 
        || {'lat': 40.8138912, 'lon': -73.9624327}; // defaults to nyc

    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name || "";
    self.submitter_email = localStorage.email || "";
    
    // Init if unsynced is undefined
    if (!localStorage.unsynced) {
        localStorage.unsynced = JSON.stringify({});
    }
    // Load up any unsynced submissions
    App.unsynced = JSON.parse(localStorage.unsynced)[self.survey.id] || []; 

    // Load up any unsynced facilities
    App.unsynced_facilities = 
        JSON.parse(localStorage.unsynced_facilities || "{}");

    // Load any facilities
    App.facilities = JSON.parse(localStorage.facilities || "{}");
    if (JSON.stringify(App.facilities) === "{}" && navigator.onLine) {
        // See if you can get some new facilities
        getNearbyFacilities(start_loc.lat, start_loc.lon, 
            FAC_RAD, // Radius in km 
            NUM_FAC, // limit
            null// what to do with facilities 
        );
    }

    // AppCache updates
    window.applicationCache.addEventListener('updateready', function() {
        alert('app updated, reloading...');
        window.location.reload();
    });

    $('header')
        .on('click', '.menu', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();
        });

    $('header')
        .on('click', '.menu_clear', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            localStorage.clear();
            App.splash();
            App.message('All survey data erased.', 'Surveys Nuked', 'message-warning');
        });

    $('header')
        .on('click', '.menu_restart', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            App.survey.clearState();
            App.splash();
            App.message('Active survey has been cleared.', 'Survey Reset', 'message-warning');
        });

    $('header')
        .on('click', '.menu_save', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            App.survey.saveState();
            App.message('Active survey has been saved.', 'Survey Saved', 'message-success');
        });
        
    App.splash();
};

App.sync = function() {
    var self = this;
    //$('.submit_modal')[0].click(); // Pop Up Submitting Modal
    self.countdown = App.unsynced.length; //JS is single threaded no race condition counter
    self.count = App.unsynced.length; //JS is single threaded no race condition counter
    var endSync = function() {
        //$('.submit_modal')[0].click(); // Remove submitting modal;
        App.splash();
        if (!App.unsynced.length) {
            App.message('All ' + self.count + ' surveys synced succesfully.', 'Survey Synced', 'message-success');
        } else {
            App.message(App.unsynced.length + ' survey(s) failed to sync succesfully. Please try again later.', 'Survey Sync Failed', 'message-error');
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

            function(survey) { 
                console.log('fail');
                --self.countdown; 

                if (self.countdown === 0) {
                    endSync();
                }
            } 
        );
    });

    // Facilities junk
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });
};

App.message = function(text, title, style) {
    // Shows a message to user
    // E.g. "Your survey has been submitted"
    $('.message_btn')[0].click();
    
    $('.modal_header').empty()
        //XXX Look into doing this in a more clean way
        .removeClass('message-primary')
        .removeClass('message-error')
        .removeClass('message-warning')
        .removeClass('message-success')
        .addClass(style)
        .text(title);


    // Message text region
    $('.message')
        .text(text);
};

App.splash = function() {
    $('header').removeClass('title-extended');
    $('.title_menu').hide();
    var self = this;
    var survey = self.survey;
    $('.overlay').hide(); // Always remove overlay after moving

    // Update page nav bar
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
            App.survey.render(App.survey.first_question, Widgets);
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
                // Reload page to update template values
                App.splash();
            } else {
                App.message('Please connect to the internet first.', 'Connection Error', 'message-warning');
            }
        });
};

App.submit = function(survey, done, fail) {
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    
    // Update submit time
    survey.submission_time = new Date().toISOString();

    $.ajax({
        url: '/api/surveys/'+survey.survey_id+'/submit',
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
        error: function() {
            fail(survey);
        }
    });

    console.log('synced submission:', survey);
    console.log('survey', '/api/surveys/'+survey.survey_id+'/submit');
}

exports.App = App;
