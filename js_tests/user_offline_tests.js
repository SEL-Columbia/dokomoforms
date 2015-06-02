var jsdom = require('jsdom');
var should = require('should');
global.window = require('./emulate_dom.js');

document = window.document;
raw_survey = null;
L = window.L;
_ = window._;
$ = window.$;
alert = window.alert;
setInterval = function(hey, you) {  } //console.log('pikachu'); }
console = window.console;
Image = window.Image;
navigator = window.navigator;
localStorage = {};

var mah_code = require('../dokomoforms/static/application.js');
App = mah_code.App;
Survey = mah_code.Survey;
Widgets = mah_code.Widgets;


// User interaction, "trigger" tests when submitting offline
describe('User offline submits tests', function(done) {

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        $.mockjax.clear();
        $(".page_nav__next").off(); //XXX Find out why events are cached
        $(".page_nav__prev").off();
        localStorage.setItem = function(id, data) {
            localStorage[id] = data;
        }
        raw_survey = require('./fixtures/survey.json');
        raw_survey.survey_metadata.location.lat = 40.80250524727603
        raw_survey.survey_metadata.location.lon =  -73.93695831298828
        App.init(raw_survey)
        App.unsynced = require('./fixtures/unsynced.json');
        navigator.onLine = false;
        done();
    });

    afterEach(function(done) {
        raw_survey = null;
        localStorage = {};
        $(".page_nav__next").off('click'); //XXX Find out why events are cached
        $(".page_nav__prev").off('click');
        $(".message").clearQueue().text("");
        $('.content').empty();
        $.mockjax.clear();
        App.unsynced = [];
        navigator.onLine = false;
        done();
    });

    it('should fail to show sync survey button when offline', 
        function(done) {
            navigator.onLine = false;
            App.unsynced.length.should.match(3);
            $.mockjax({
                  url: '',
                  status: 200,
                  onAfterSuccess: function() { 
                    //$('.message').text().should.match('Survey submitted!'); 
                    //done();
                    assert(false, "Post snuck through"); 
                  },
                  onAfterError: function() { 
                      //assert(false, "Failed to catch post correctly"); 
                      assert(false, "Post snuck through"); 

                  },
                  responseText: {
                      status: "success",
                  }
            });

            var survey = App.survey;
            var questions = survey.questions;

            $('.sync_btn').length.should.match(0); // Sync the survey;

            App.unsynced.length.should.match(3);
            done();
    });

    it('should fail to sync ANY unsynced survey when each post 500s', 
        function(done) {
            var self = this;
            navigator.onLine = true;
            App.splash();
            self.counter = 3;
            App.unsynced.length.should.match(3);
            $.mockjax({
                  url: '/api/surveys/f5a35e4f-c5dc-4fb8-a768-ed6d92df2b1a/submit',
                  status: 500,
                  onAfterSuccess: function() { 
                    assert(false, "Post snuck through"); 
                  },
                  onAfterError: function() { 
                      --self.counter;
                      if(self.counter === 0) {
                        App.unsynced.length.should.match(3);
                        done();
                      }
                  },
                  responseText: {
                      status: "success",
                  }
            });

            var survey = App.survey;
            var questions = survey.questions;
            console.log($('.sync_btn').length);
            $('.sync_btn').click(); // Sync the survey;
    });
});
