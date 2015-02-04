var jsdom = require('jsdom');
var should = require('should');
var request = require('supertest');
var assert = require('assert');

describe('App and Survey Init Tests', function(done) {
    // globals
    var window;
    var raw_survey;

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        jsdom.env('./tests/widgets.html',  
            ['../static/lib.js', 'classList_shim.js', '../static/app.js'], 
            function(error, win) {
                if (error) throw (error);
            
                window = win;
                window.localStorage = {};
                done();
            });

    });

    afterEach(function(done) {
        raw_survey = null;
        window.close();
        window = null;
        done();
    });

    it('should init app and survey juust fine', 
        function(done) {
            window.App.init(raw_survey);
            raw_survey.metadata.location.should.match(window.App.start_loc);
            should(window.App.survey).be.ok;

            var survey = window.App.survey;
            should(survey.id).match(raw_survey.survey_id);
            should(survey.questions).match(raw_survey.questions);
            should(survey.metadata).match(raw_survey.metadata);
            done();
        });

    it('should order the survey questions just fine', 
        function(done) {
            window.App.init(raw_survey);
            var survey = window.App.survey;
            
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
    
});


describe('Survey function tests', function(done) {
    // globals
    var window;
    var raw_survey;

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        jsdom.env('./tests/widgets.html',  
            ['../static/lib.js', 'classList_shim.js', '../static/app.js'], 
            function(error, win) {
                if (error) throw (error);
            
                window = win;
                window.localStorage = {};
                done();
            });

    });

    afterEach(function(done) {
        raw_survey = null;
        window.close();
        window = null;
        done();
    });

    it('hasOneResponse: should return false for invalid input true otherwise',
        function(done) {
            var questions = [
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "integer",
                    sequence_number: 1
                },
            ];

            var survey = new window.Survey("id", questions, {});

            // empty
            survey.hasOneResponse(questions[0]).should.match(false);
            // O value
            questions[0].answer = [0];
            survey.hasOneResponse(questions[0]).should.match(true);
            // some value
            questions[0].answer = [1];
            survey.hasOneResponse(questions[0]).should.match(true);
            // empty string
            questions[0].answer = [""];
            survey.hasOneResponse(questions[0]).should.match(false);
            // incorrect type (get hasOneResponse does not validate type)
            questions[0].answer = ["bs"];
            survey.hasOneResponse(questions[0]).should.match(true);

            done();

        });

    
    it('next: should enforce required questions',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "text",
                    logic: {required: true},
                    sequence_number: 1
                },
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "integer",
                    sequence_number: 2
                },
            ];

            var survey = new window.Survey("id", questions, {});
            console.log(survey.next(NEXT));

            done();

        });
    
});


describe('Next Question Tests', function(done) {
    // globals
    var window;
    var raw_survey;

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        jsdom.env('./tests/widgets.html',  
            ['../static/lib.js', 'classList_shim.js', '../static/app.js'], 
            function(error, win) {
                if (error) throw (error);
            
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
