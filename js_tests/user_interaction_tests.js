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

var mah_code = require('../dokomoforms/static/app.js');
var App = mah_code.App;
var Survey = mah_code.Survey;
var Widgets = mah_code.Widgets;


// User interaction, "trigger" tests
describe('User next/prev tests', function(done) {

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        $(".page_nav__next").off(); //XXX Find out why events are cached
        $(".page_nav__prev").off();
        raw_survey = require('./fixtures/survey.json');
        raw_survey.survey_metadata.location.lat = 40.80250524727603
        raw_survey.survey_metadata.location.lon =  -73.93695831298828
        App.init(raw_survey)
        done();
    });

    afterEach(function(done) {
        raw_survey = null;
        localStorage = {};
        done();
    });

    it('should move from question 0 to 1 when next is clicked', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            var first_question = questions[0];
            var second_question = questions[1];

            first_question.should.equal(survey.current_question);

            $(".page_nav__next").trigger("click");

            first_question.should.not.equal(survey.current_question);
            second_question.should.equal(survey.current_question);

            done();
        });

    it('should move from last question to submit page when next is clicked',
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            var last_question = questions[questions.length - 1];
            
            survey.render(last_question);
            last_question.should.equal(survey.current_question);

            $(".page_nav__next").trigger("click");

            // current question should remain the same on submitters page
            last_question.should.equal(survey.current_question);
            $(".question__title").html().trim()
                .should.equal("That's it, you're finished!");

            done();
        });

    it('should move from question 0 to nowhere when prev is clicked', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            var first_question = questions[0];

            first_question.should.equal(survey.current_question);
            var title = $(".question__title").html();

            $(".page_nav__prev").trigger("click");
            first_question.should.equal(survey.current_question);
            $(".question__title").html().trim().should.equal(title);

            done();
        });

    it('should move from submit page to current question when prev is clicked', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;
            
            var last_question = questions[questions.length - 1];
            survey.current_question = last_question;
            var title = "another facility question";

            // render submit page
            survey.next(1);
            last_question.should.equal(survey.current_question);

            // Now move back
            $(".page_nav__prev").trigger("click");
            last_question.should.equal(survey.current_question);
            $(".question__title").html().trim().should.match(title);
            done();
        });

    it('should move from question 0 to 1 then back while maintaining answer value inputted at 0', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            var first_question = questions[0];
            var second_question = questions[1];

            first_question.should.equal(survey.current_question);

            $("input").val("1").trigger("change");
            first_question.answer[0].response.should.equal(1);

            $(".page_nav__next").trigger("click");

            first_question.should.not.equal(survey.current_question);
            second_question.should.equal(survey.current_question);

            $(".page_nav__prev").trigger("click");

            first_question.should.equal(survey.current_question);
            second_question.should.not.equal(survey.current_question);

            first_question.answer[0].response.should.equal(1);
            $("input").val().should.equal("1");
            done();
        });
});

describe('User submission tests', function(done) {
    before(function(done) {
        done();
    });


    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        localStorage.name = 'viktor sucks';
        App.init(raw_survey);
        done();
    });

    afterEach(function(done) {
        raw_survey = null;
        localStorage = {};
        done();
    });

    it('should preload submitter name', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;
            var name = App.submitter_name;
            
            survey.render(undefined);
            $(".question__title").html().trim()
                .should.equal("That's it, you're finished!");

            $(".name_input").val()
                .should.equal(name);

            done();
    });

    it('should update submitter name', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;
            var name = App.submitter_name;
            var new_name = '2chains'
            
            survey.render(undefined);
            $(".question__title").html().trim()
                .should.equal("That's it, you're finished!");

            $(".name_input").val(new_name)
            $(".name_input").trigger('keyup');

            // No references to old name
            $(".name_input").val()
                .should.not.equal(name);

            localStorage.name.should.not.equal(name);
            App.submitter_name.should.not.equal(name);

            // all the references
            localStorage.name.should.equal(new_name);
            $(".name_input").val().should.equal(new_name);
            App.submitter_name.should.equal(new_name);

            done();
        });
});

describe('User multiple choice tests', function(done) {

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        $(".page_nav__next").off(); //XXX Find out why events are cached
        $(".page_nav__prev").off();
        raw_survey = require('./fixtures/survey.json');
        App.init(raw_survey)
        done();
    });

    afterEach(function(done) {
        raw_survey = null;
        localStorage = {};
        done();
    });

    it('should remember choice a was selected', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            //XXX: Straight out of raw_surveys, update these when updating survey.json
            var choices = [
                {"question_choice_id":"8ffa4051-09bb-4966-bc77-098e40cbee27","choice":"choice a","choice_number":1},
                {"question_choice_id":"e9cb9ea8-4d8f-4f7a-b669-689f15835bbc","choice":"choice b","choice_number":2}
            ];

            var first_question = questions[0];
            var mc_question = questions[7];

            survey.render(mc_question);

            first_question.should.not.equal(survey.current_question);
            mc_question.should.equal(survey.current_question);

            $('.question__select').val("8ffa4051-09bb-4966-bc77-098e40cbee27").change();
            mc_question.answer[0].response.should.match("8ffa4051-09bb-4966-bc77-098e40cbee27");

            $(".page_nav__next").trigger("click");
            mc_question.should.not.equal(survey.current_question);
            $(".page_nav__prev").trigger("click");
            mc_question.should.equal(survey.current_question);

            $('.question__select').val().should.match("8ffa4051-09bb-4966-bc77-098e40cbee27");
            mc_question.answer[0].response.should.match("8ffa4051-09bb-4966-bc77-098e40cbee27");

            done();

           
        });

    it('should remember choice other was selected', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            //XXX: Straight out of raw_surveys, update these when updating survey.json
            var choices = [
                {"question_choice_id":"8ffa4051-09bb-4966-bc77-098e40cbee27","choice":"choice a","choice_number":1},
                {"question_choice_id":"e9cb9ea8-4d8f-4f7a-b669-689f15835bbc","choice":"choice b","choice_number":2}
            ];

            var first_question = questions[0];
            var mc_question = questions[7];

            survey.render(mc_question);

            first_question.should.not.equal(survey.current_question);
            mc_question.should.equal(survey.current_question);

            $('.question__select').val("other").change();
            $('.text_input').val("poop").change();

            mc_question.answer[choices.length].response.should.match("poop");

            $(".page_nav__next").trigger("click");
            mc_question.should.not.equal(survey.current_question);
            $(".page_nav__prev").trigger("click");
            mc_question.should.equal(survey.current_question);

            $('.question__select').val().should.match("other");
            mc_question.answer[choices.length].response.should.match("poop");

            done();
           
        });

    it('should NOT remember choice other was selected', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            //XXX: Straight out of raw_surveys, update these when updating survey.json
            var choices = [
                {"question_choice_id":"8ffa4051-09bb-4966-bc77-098e40cbee27","choice":"choice a","choice_number":1},
                {"question_choice_id":"e9cb9ea8-4d8f-4f7a-b669-689f15835bbc","choice":"choice b","choice_number":2}
            ];

            var first_question = questions[0];
            var mc_question = questions[7];

            survey.render(mc_question);

            first_question.should.not.equal(survey.current_question);
            mc_question.should.equal(survey.current_question);

            $('.question__select').val("other").change();
            $('.text_input').val("").change(); // No value ==> you didn't fill out other

            $(".page_nav__next").trigger("click");
            mc_question.should.not.equal(survey.current_question);
            $(".page_nav__prev").trigger("click");
            mc_question.should.equal(survey.current_question);

            $('.question__select').val().should.match("null"); //Go back to the "Please pick option" thing

            done();
   });

});

describe('User facility questions', function(done) {

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        $(".page_nav__next").off(); //XXX Find out why events are cached
        $(".page_nav__prev").off();
        raw_survey = require('./fixtures/survey.json');
        App.init(raw_survey)
        App.facilities = require('./fixtures/facilities.json');
        done();
    });

    afterEach(function(done) {
        raw_survey = null;
        localStorage = {};
        done();
    });

    it('should pick an existing facility', 
        function(done) {
            var survey = App.survey;
            var questions = survey.questions;

            var first_question = questions[0];
            var fac_question = questions[questions.length - 1];

            survey.render(fac_question);

            first_question.should.not.equal(survey.current_question);
            fac_question.should.equal(survey.current_question);

            //$('.leaflet-marker-icon').first().click();
            //console.log($('.facility__name').val());
            //$('.leaflet-marker-icon').first().click();
            //console.log($('.facility__name').val());
            
            done();

   });
});
