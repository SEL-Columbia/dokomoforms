var jsdom = require('jsdom');
var should = require('should');
var request = require('supertest');

// User interaction, "window.trigger" tests
describe('User next/prev tests', function(done) {
    // globals
    var window;
    var raw_survey;

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        jsdom.env('./test/widgets.html',  
            [//'lib/blanket.min.js', 
            'lib/classList_shim.js',
            '../static/lib.js',  
            '../static/app.js'], 
            function(error, win) {
                if (error) { 
                    console.log(error);
                    throw (error) 
                }
            
                window = win;
                window.localStorage = {};
                window.App.init(raw_survey)
                done();
            });

    });

    afterEach(function(done) {
        raw_survey = null;
        window.close();
        window = null;
        done();
    });

    it('should move from question 0 to 1 when next is clicked', 
        function(done) {
            var survey = window.App.survey;
            var questions = survey.questions;

            var first_question = questions[0];
            var second_question = questions[1];

            first_question.should.equal(survey.current_question);

            window.$(".page_nav__next").trigger("click");

            first_question.should.not.equal(survey.current_question);
            second_question.should.equal(survey.current_question);

            done();
        });

    it('should move from last question to submit page when next is clicked',
        function(done) {
            var survey = window.App.survey;
            var questions = survey.questions;

            var last_question = questions[questions.length - 1];
            
            survey.render(last_question);
            last_question.should.equal(survey.current_question);

            window.$(".page_nav__next").trigger("click");

            // current question should remain the same on submitters page
            last_question.should.equal(survey.current_question);
            window.$(".question__title").html().trim()
                .should.equal("That's it, you're finished!");

            done();
        });

    it('should move from question 0 to nowhere when prev is clicked', 
        function(done) {
            var survey = window.App.survey;
            var questions = survey.questions;

            var first_question = questions[0];

            first_question.should.equal(survey.current_question);
            var title = window.$(".question__title").html();

            window.$(".page_nav__prev").trigger("click");
            first_question.should.equal(survey.current_question);
            window.$(".question__title").html().trim().should.equal(title);

            done();
        });

    it('should move from submit page to current question when prev is clicked', 
        function(done) {
            var survey = window.App.survey;
            var questions = survey.questions;
            
            var last_question = questions[questions.length - 1];
            survey.current_question = last_question;
            var title = "another note";

            // render submit page
            survey.render(undefined);
            last_question.should.equal(survey.current_question);

            // Now move back
            window.$(".page_nav__prev").trigger("click");
            last_question.should.equal(survey.current_question);
            window.$(".question__title").html().trim().should.match(title);
            done();
        });
});

describe('User submission tests', function(done) {
    // globals
    var window;
    var raw_survey;

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        jsdom.env('./test/widgets.html',  
            [//'lib/blanket.min.js', 
            'lib/classList_shim.js',
            '../static/lib.js',  
            '../static/app.js'], 
            function(error, win) {
                if (error) { 
                    console.log(error);
                    throw (error) 
                }
            
                window = win;
                window.localStorage = {'name': 'hello'};
                window.App.init(raw_survey)
                done();
            });

    });

    afterEach(function(done) {
        raw_survey = null;
        window.close();
        window = null;
        done();
    });

    it('should preload submitter name', 
        function(done) {

            var survey = window.App.survey;
            var questions = survey.questions;
            var name = window.App.submitter_name;
            
            survey.render(undefined);
            window.$(".question__title").html().trim()
                .should.equal("That's it, you're finished!");

            window.$(".name_input").val()
                .should.equal(name);

            done();
        });

    it('should update submitter name', 
        function(done) {

            var survey = window.App.survey;
            var questions = survey.questions;
            var name = window.App.submitter_name;
            var new_name = '2chains'
            
            survey.render(undefined);
            window.$(".question__title").html().trim()
                .should.equal("That's it, you're finished!");

            window.$(".name_input").val(new_name)
            window.$(".name_input").trigger('keyup');

            // No references to old name
            window.$(".name_input").val()
                .should.not.equal(name);
            window.localStorage.name.should.not.equal(name);
            window.App.submitter_name.should.not.equal(name);

            // all the references
            window.localStorage.name.should.equal(new_name);
            window.$(".name_input").val()
                .should.equal(new_name);
            window.App.submitter_name.should.equal(new_name);

            done();
        });
});
