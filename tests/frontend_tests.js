var jsdom = require('jsdom');
var should = require('should');
var request = require('supertest');
var assert = require('assert');


// globals
var window;
var survey = require('./fixtures/survey.json');

describe('Next Question Tests', function(done) {
    before(function(done) {
        jsdom.env('./tests/widgets.html',  ['../static/lib.js', 'classList_shim.js', '../static/app.js'], 
            function(error, win) {
                if (error) throw (error);
            
                window = win;
                done();
            });
    });

    beforeEach(function(done) {
        window.localStorage = {};
        window.App.init(survey)
        done();
    });

    afterEach(function(done) {
        done();
    });

    describe('Simple Move Question', function() {
        it('should move from question 0 to 1 when next is clicked', function(done) {

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

        it('should move from last question to submit page when next is clicked', function(done) {
            var survey = window.App.survey;
            var questions = survey.questions;

            var last_question = questions[questions.length - 1];
            
            survey.render(last_question);
            last_question.should.equal(survey.current_question);

            window.$(".page_nav__next").trigger("click");

            // current question should remain the same on submitters page
            last_question.should.equal(survey.current_question);
            window.$(".question__title").html().trim().should.equal("That's it, you're finished!");

            done();
        });

        it('should move from question 0 to nowhere when prev is clicked', function(done) {

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

        it('should move from submit page to current question when prev is clicked', function(done) {
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
});

