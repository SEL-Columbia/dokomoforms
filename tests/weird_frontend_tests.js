var jsdom = require('jsdom');
var should = require('should');
var request = require('supertest');
var assert = require('assert');
var fs = require('fs');

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
            ['lib/classList_shim.js',
            '../static/lib.js'], 
            function(error, win) {
                if (error) throw (error);
                window = win;
                var document = window.document;

                var features = document.implementation._features;
                document.implementation.addFeature('FetchExternalResources', ['script']);
                document.implementation.addFeature('ProcessExternalResources', ['script']);
                document.implementation.addFeature('MutationEvents', ['2.0']);

                var script = window.document.createElement('script');
                script.onload = function() {
                    document.implementation._features = features;
                };
                script.text = fs.readFileSync("tests/lib/blanket.min.js", "utf-8");
                window.document.body.appendChild(script);

                window.localStorage = {};
                var script = window.document.createElement('script');
                script.setAttribute('data-cover', '');
                script.onload = function() {
                    document.implementation._features = features;
                };
                script.text = fs.readFileSync("static/app.js", "utf-8");
                window.document.body.appendChild(script);

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
            ['lib/classList_shim.js',
            '../static/lib.js'], 
            function(error, win) {
                if (error) throw (error);
                window = win;
                var document = window.document;

                var features = document.implementation._features;
                document.implementation.addFeature('FetchExternalResources', ['script']);
                document.implementation.addFeature('ProcessExternalResources', ['script']);
                document.implementation.addFeature('MutationEvents', ['2.0']);

                var script = window.document.createElement('script');
                script.onload = function() {
                    document.implementation._features = features;
                };
                script.text = fs.readFileSync("tests/lib/blanket.min.js", "utf-8");
                window.document.body.appendChild(script);

                window.localStorage = {};
                var script = window.document.createElement('script');
                script.setAttribute('data-cover', '');
                script.onload = function() {
                    document.implementation._features = features;
                };
                script.text = fs.readFileSync("static/app.js", "utf-8");
                window.document.body.appendChild(script);

                done();
            });

    });

    afterEach(function(done) {
        raw_survey = null;
        window.close();
        window = null;
        done();
    });

    it('getFirstResponse: should return null if theres no valid integer input',
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
            should(survey.getFirstResponse(questions[0])).not.be.ok;
            // O value
            questions[0].answer = [0];
            should(survey.getFirstResponse(questions[0])).match(0);;
            // some value
            questions[0].answer = [1];
            should(survey.getFirstResponse(questions[0])).be.ok;
            // empty string
            questions[0].answer = [""];
            should(survey.getFirstResponse(questions[0])).not.be.ok;
            // incorrect type (get getFirstResponse does not validate type)
            questions[0].answer = ["bs"];
            should(survey.getFirstResponse(questions[0])).not.be.ok;

            done();

        });
    
    it('getFirstResponse: should return null if theres no valid text input',
        function(done) {
            var questions = [
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "text",
                    sequence_number: 1
                },
            ];

            var survey = new window.Survey("id", questions, {});

            // empty
            should(survey.getFirstResponse(questions[0])).not.be.ok;
            // empty string
            questions[0].answer = [""];
            should(survey.getFirstResponse(questions[0])).not.be.ok;
            // valid 
            questions[0].answer = ["bs"];
            should(survey.getFirstResponse(questions[0])).be.ok;

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
            questions[0].should.equal(survey.current_question);

            // state shouldn't change
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);
            
            // state SHOULD change
            questions[0].answer = ["yo"];
            survey.next(NEXT);
            questions[0].should.not.equal(survey.current_question);
            questions[1].should.equal(survey.current_question);

            done();

        });
    
    it('next: should enforce required correctly for falsy response 0',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "integer",
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
            questions[0].should.equal(survey.current_question);

            // state shouldn't change
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);
            
            // state SHOULD change
            questions[0].answer = [0];
            survey.next(NEXT);
            questions[0].should.not.equal(survey.current_question);
            questions[1].should.equal(survey.current_question);

            done();

        });
    
    it('next: should enforce required correctly for falsy response ""',
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
            questions[0].should.equal(survey.current_question);

            // state shouldn't change
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);
            
            // state SHOULDNT change
            questions[0].answer = [""];
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);

            done();

        });
    
    it('next: should enforce required correctly for invalid input to decimal',

        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "decimal",
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
            questions[0].should.equal(survey.current_question);

            // state shouldn't change
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);
            
            // state SHOULDNT change
            questions[0].answer = ["decimal"];
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);


            done();

        });
    
    it('next: should enforce required correctly for invalid input to date',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "date",
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
            questions[0].should.equal(survey.current_question);

            // state shouldn't change
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);
            
            // state SHOULDNT change
            //questions[0].answer = ["date"];
            //survey.next(NEXT);
            //questions[0].should.equal(survey.current_question);
            //questions[1].should.not.equal(survey.current_question);
            //XXX VALIDATION FOR TIME NOT DONE;


            done();

        });
    
    it('next: should enforce required correctly for invalid input to time',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "time",
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
            questions[0].should.equal(survey.current_question);

            // state shouldn't change
            survey.next(NEXT);
            questions[0].should.equal(survey.current_question);
            questions[1].should.not.equal(survey.current_question);
            
            // state SHOULDNT change
            //questions[0].answer = ["time"];
            //survey.next(NEXT);
            //questions[0].should.equal(survey.current_question);
            //questions[1].should.not.equal(survey.current_question);
            //XXX: VALIDATION FOR DATE NOT DONE;


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
            ['lib/classList_shim.js',
            '../static/lib.js'], 
            function(error, win) {
                if (error) throw (error);
                window = win;
                var document = window.document;

                var features = document.implementation._features;
                document.implementation.addFeature('FetchExternalResources', ['script']);
                document.implementation.addFeature('ProcessExternalResources', ['script']);
                document.implementation.addFeature('MutationEvents', ['2.0']);

                var script = window.document.createElement('script');
                script.onload = function() {
                    document.implementation._features = features;
                };
                script.text = fs.readFileSync("tests/lib/blanket.min.js", "utf-8");
                window.document.body.appendChild(script);

                window.localStorage = {};
                var script = window.document.createElement('script');
                script.setAttribute('data-cover', '');
                script.onload = function() {
                    document.implementation._features = features;
                };
                script.text = fs.readFileSync("static/app.js", "utf-8");
                window.document.body.appendChild(script);
                
                window.App.init(raw_survey);
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
