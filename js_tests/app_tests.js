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
navigator = window.navigator;
    
var mah_code = require('../dokomoforms/static/bundle.js');
var App = mah_code.App;
var Survey = mah_code.Survey;
var Widgets = mah_code.Widgets;

// Creating the app and loading up survey questions
describe('App initalization Tests', function(done) {
    var survey_id = "ce76f2ec-0340-498a-9d31-75eedc9d5916";
    var integer_id = "c84962e3-5525-4503-9414-c6d92db43770";
    var text_id = "a45ffa59-1132-4a46-b3be-35644c13bb80";
    var location_id = "d5c1e438-fa57-41f7-bc4a-da69f6b96ba2";

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
            answers = {}
            answers[integer_id] = [{response: 123},{response:null},{response:123123}, null],
            answers[location_id] = [{response:{'lon':-73.965, 'lat': 40.80}}],
            answers[text_id] = [null,null,{response:"ewrwrwr"}],
            
            localStorage[survey_id] = 
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

            response = App.survey.questions[5].answer[0].response.lon;
            response.should.match(-73.965);

            response = App.survey.questions[6].answer[0].response;
            response.should.match("ewrwrwr"); // Confirm response moved to first slot


            done();
        });
    
});


