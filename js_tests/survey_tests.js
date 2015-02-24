var jsdom = require('jsdom');
var should = require('should');
global.window = require('./emulate_dom.js');

document = window.document;
L = window.L;
_ = window._;
$ = window.$;
alert = window.alert;
setInterval = function(hey, you) {  } //console.log('pikachu'); }
console = window.console;
Image = window.Image;
navigator = window.navigator;
localStorage = {};
setTimeout = function(cb, time) { cb(); };

var mah_code = require('../static/app.js');
var App = mah_code.App;
var Survey = mah_code.Survey;
var Widgets = mah_code.Widgets;

var survey = null;

// Most important tests, survey functions
describe('Survey unit and regression tests', function(done) {
    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        localStorage = {};
        localStorage.setItem = function(id, data) {
            localStorage[id] = data;
        }

        App.facilities = [];
        App.unsynced_facilities = {};

        done();
    });

    afterEach(function(done) {
        $(".page_nav__next").off('click'); //XXX Find out why events are cached
        $(".page_nav__prev").off('click');
        $(".message").clearQueue().text("");
        $('.content').empty();
        survey = null;
        done();
    });
    
    after(function(done) {
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

            survey = new Survey("id", questions, {});

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

            survey = new Survey("id", questions, {});

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
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
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
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
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
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
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
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
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
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
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
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
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
            //XXX: VALIDATION FOR DATE NOT ENFORCED;


            done();

        });
    
    it('next: should follow sequence number ordering not list ordering',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "time",
                    logic: {},
                    sequence_number: 1
                },
                {
                    question_to_sequence_number: 4,
                    type_constraint_name: "text",
                    logic: {},
                    sequence_number: 3
                },
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "integer",
                    logic: {},
                    sequence_number: 4
                },
                {
                    question_to_sequence_number: 3,
                    type_constraint_name: "decimal",
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
            questions[0].should.equal(survey.current_question);

            survey.next(NEXT);
            questions[3].should.equal(survey.current_question);
            
            survey.next(NEXT);
            questions[1].should.equal(survey.current_question);

            survey.next(NEXT);
            questions[2].should.equal(survey.current_question);
            
            survey.next(PREV);
            questions[1].should.equal(survey.current_question);

            survey.next(PREV);
            questions[3].should.equal(survey.current_question);

            survey.next(PREV);
            questions[0].should.equal(survey.current_question);
            done();

        });

    it('next: should follow new paths when answer branches',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "time",
                    logic: {},
                    sequence_number: 1
                },
                {
                    question_to_sequence_number: 4,
                    type_constraint_name: "text",
                    logic: {},
                    sequence_number: 3
                },
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "text",
                    logic: {},
                    sequence_number: 5
                },
                {
                    question_to_sequence_number: 5,
                    type_constraint_name: "text",
                    logic: {},
                    sequence_number: 4
                },
                {
                    question_to_sequence_number: 3,
                    type_constraint_name: "text", //code doesnt assert that its multiple choice
                    logic: {},
                    branches: [
                        {
                            question_choice_id: "end", // pretend this is a uuid
                            to_sequence_number: 5,
                        },
                        {
                            question_choice_id: "skip", // fake uuid
                            to_sequence_number: 4,
                        }
                    ],
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
            var brancher = questions[4];
            var next = questions[1];
            var end = questions[2];
            var skip = questions[3];

            questions[0].should.equal(survey.current_question);
            survey.next(NEXT);

            // assert we are at branching question
            brancher.should.equal(survey.current_question);
            // follows normal seq path
            survey.next(NEXT);
            next.should.equal(survey.current_question);
            // assert we are back
            survey.next(PREV);
            brancher.should.equal(survey.current_question);
            // branch to end 
            brancher.answer = ["end"];
            survey.next(NEXT); 
            end.should.equal(survey.current_question);
            // come back
            survey.next(PREV);
            brancher.should.equal(survey.current_question);
            // branch to skip 
            brancher.answer = ["skip"];
            survey.next(NEXT); 
            skip.should.equal(survey.current_question);
            // come back again fine
            survey.next(PREV);
            brancher.should.equal(survey.current_question);
            

            done();

        });

    it('submit: empty submission',
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "time",
                    logic: {},
                    sequence_number: 1
                },
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "integer",
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
            survey.submit();
            $('.message').text().should.match("Submission failed, No questions answer in Survey!");
            done();

        });

    it('submit: basic submission',
        //XXX: Fake response so that this doesn't 404
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: 2,
                    type_constraint_name: "text",
                    logic: {},
                    sequence_number: 1
                },
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "integer",
                    logic: {},
                    sequence_number: 2
                },
            ];

            survey = new Survey("id", questions, {});
            questions[0].answer = ["hey baby"];
            survey.submit();
            //XXX$('.message').text().should.match('Survey submitted!');
            $('.message').text().should.match("Submission failed, will try again later.");
            done();

        });


    it('submit: facility submission',
        //XXX: Fake response so that this doesn't 404
        //XXX: Fake revisit response so that this doesn't 404
        function(done) {
            var NEXT = 1;
            var PREV = -1;
            var questions = [
                {
                    question_to_sequence_number: -1,
                    type_constraint_name: "facility",
                    logic: {},
                    answer: [],
                    question_title: "fac",
                    sequence_number: 1
                },
            ];

            console.log(App.facilities)
            console.log(App.unsynced_facilities)

            // Preload some facilities;
            App.unsynced_facilities[1] = {
                'name': 'New Facility', 'uuid': 1, 
                'properties' : {'sector': 'health'},
                'coordinates' : [40.01, 70.01]
            };

            survey = new Survey("id", questions, {});
            questions[0].answer = [[1, [40.01, 70.01]]]; //So many arrays

            survey.submit();
            //XXX$('.message').text().should.match('Survey submitted!'); 
            //XXX should(App.unsynced_facilities[1]).not.be.ok;
            //XXX App.facilities.should.have.length(1);
            $('.message').text().should.match("Submission failed, will try again later."); 
            done();

        });
});

