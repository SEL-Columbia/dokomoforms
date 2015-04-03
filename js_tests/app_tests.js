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
localStorage = {};
    
var mah_code = require('../dokomoforms/static/app.js');
var App = mah_code.App;
var Survey = mah_code.Survey;
var Widgets = mah_code.Widgets;

// Creating the app and loading up survey questions
describe('App initalization Tests', function(done) {

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        done();
    });

    afterEach(function(done) {
        $(".page_nav__next").off('click');//XXX Find out why events are cached across windows
        $(".page_nav__prev").off('click'); //(removing cached require not enough); 
        raw_survey = null;
        localStorage = {};
        done();
    });

    it('should init app and survey juust fine', 
        function(done) {
            App.init(raw_survey);
            raw_survey.survey_metadata.location.should.match(App.start_loc);
            should(App.survey).be.ok;

            var survey = App.survey;
            should(survey.id).match(raw_survey.survey_id);
            should(survey.questions).match(raw_survey.questions);
            should(survey.metadata).match(raw_survey.survey_metadata);
            done();
        });

    it('should order the survey questions just fine', 
        function(done) {
            App.init(raw_survey);
            var survey = App.survey;
            
            var question = survey.current_question;
            var sequence_num = 1;

            var len = survey.questions.length;

            while(question) {
                sequence_num.should.match(question.sequence_number);
                sequence_num++;
                question = question.next;
            }

            sequence_num.should.match(len + 1);
            done();
        });
    
    it('should fill in submitter name', 
        function(done) {
            var name = 'viktor sucks';
            localStorage['name'] = name;
            App.init(raw_survey);
            App.submitter_name.should.match(name);
            done();
        });

    it('should load previous submission values',
            //XXX:maybe it shouldn't?
        function(done) {
            answers = {
                "22a915d2-19cd-4de3-8225-aaecc7a90c1b":[{response: 123},{response:null},{response:123123}, null],
                "6a4036b4-881b-4838-8cf6-4948cb113077":[{response:{'lon':-73.965, 'lat': 40.80}}],
                "0c8a62fa-7859-424e-acfd-2b5c80e6a36d":[null,null,{response:"ewrwrwr"}],

            }
            
            localStorage["fc76fe08-9a6c-43cf-b30f-4b9b4ee97af2"] = 
               JSON.stringify(answers); 
            
            App.init(raw_survey);

            App.survey.render(App.survey.questions[0]); // Render does the array clean up 
            App.survey.questions[0].answer.length.should.match(2); // Null responses are wiped;)
            App.survey.render(App.survey.questions[6]); // Render does the array clean up 
            App.survey.questions[0].answer.length.should.match(2); // Null responses are wiped;)
            App.survey.render(App.survey.questions[6]); // Render does the array clean up 
            App.survey.questions[6].answer.length.should.match(1); // Null responses are wiped;)

            var response = App.survey.questions[0].answer[0].response;
            response.should.match(123);

            response = App.survey.questions[0].answer[1].response;
            response.should.match(123123); // Confirm response moved to second place

            response = App.survey.questions[2].answer[0].response.lon;
            response.should.match(-73.965);

            response = App.survey.questions[6].answer[0].response;
            response.should.match("ewrwrwr"); // Confirm response moved to first slot


            done();
        });
    
});


