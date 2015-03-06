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

var mah_code = require('../dokomoforms/static/app.js');
var Widgets = mah_code.Widgets;
var App = mah_code.App;


// Location and Facility Question rendering
describe('Widget creation tests', function(done) {
    before(function(done) {
        done();
    });


    beforeEach(function(done) {
        App.facilities = [];
        App.unsynced_facilities = {};
        done();
    });

    afterEach(function(done) {
        $(".page_nav__next").off('click'); //XXX Find out why events are cached
        $(".page_nav__prev").off('click');
        $('.content').empty();
        localStorage = {};
        done();
    });
    
    after(function(done) {
        done();
    });

    it('should render basic input widget with prepopulated answer',
        //XXX: Decimal, integer, text, time, and date all use same widget code
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {},
                answer: [{response:1.01}],
                question_title: "Whiplash was real good",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.content')
                .find('input')
                .val()
                .should.match('1.01');


            $('.question__title')
                .text()
                .should.match('Whiplash was real good');

            done();

        });
    
    it('should render basic input widget with multiple prepopulated answer',
        //XXX: Decimal, integer, text, time, and date all use same widget code
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {},
                allow_multiple: true,
                answer: [1.01, 1.02, 1.03, null, 1.05],
                question_title: "Whiplash was real good +",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.content')
                .find('input')
                .each(function(idx, elem) { 
                    if (elem.value) {
                        elem.value.should.match(String(question.answer[idx]));
                    }
                });

            $('.question__title')
                .text()
                .should.match('Whiplash was real good +');

            done();

        });

    it('should render widget with +/- buttons',
        //XXX: All inputs render +/- identically 
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {},
                allow_multiple: true,
                question_title: "Whiplash was real good +-",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.content')
                .find('.question__add')
                .length.should.equal(1);

            $('.content')
                .find('.question__minus')
                .length.should.equal(1);

            done();

    });
    
    it('should NOT render widget with +/- buttons',
        //XXX: All inputs render +/- identically 
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {},
                allow_multiple: false,
                question_title: "Whiplash was real good +-",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.content')
                .find('.question__add')
                .length.should.equal(0);

            $('.content')
                .find('.question__minus')
                .length.should.equal(0);

            done();

    });

    it('should render location widget with default location',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "location",
                logic: {},
                answer: [],
                question_title: "I'm surprised Big 6 Hero or w/e got awarded",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__lon')
                .val()
                .should.match("70");
            
            $('.question__lat')
                .val()
                .should.match("40");


            $('.question__title')
                .text()
                .should.match("I'm surprised Big 6 Hero or w/e got awarded");

            done();

        });
    
    it('should render location widget with prepopulated location',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "location",
                logic: {},
                answer: [{response:{'lon':5, 'lat':7}}],
                question_title: "Birdman was meh, clearly appealed to the judges though",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__lon')
                .val()
                .should.match("5");
            
            $('.question__lat')
                .val()
                .should.match("7");


            $('.question__title')
                .text()
                .should.match("Birdman was meh, clearly appealed to the judges though");

            $('#map').find('.leaflet-marker-icon').length.should.be.exactly(0);
            done();

        });
    
    it('should render facility widget with default location',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "facility",
                logic: {},
                answer: [],
                question_title: "Good year for flixs though",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("Good year for flixs though");

            done();

        });

    it('should render facility widget with default location and retrieve facilities',
        function(done) {
            //XXX: Fake Revisit response, make this an actual test
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "facility",
                logic: {},
                answer: [],
                question_title: "Good year for flixs though",
                sequence_number: 1
            };
            
            //XXX: Figure this out
            //navigator.onLine = true
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("Good year for flixs though");

            done();

        });
    
    it('should render facility widget with default location and some default facilities',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "facility",
                logic: {},
                answer: [],
                question_title: "Good year for flixs though+",
                sequence_number: 1
            };
            
            // Preload some facilities;
            App.facilities = require('./fixtures/facilities.json');

            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("Good year for flixs though+");

            $('#map').find('.leaflet-marker-icon').length.should.be.exactly(68); // basic check to see if markers are rendered

            done();

        });

    it('should render facility widget with default location an unsynced facility',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "facility",
                logic: {},
                answer: [],
                question_title: "That lego movie song sucks",
                sequence_number: 1
            };
            
            // Preload some facilities;
            App.unsynced_facilities[1] = {
                'name': 'New Facility', 'uuid': 1, 
                'properties' : {'sector': 'health'},
                'coordinates' : [40.01, 70.01]
            };

            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("That lego movie song sucks");

            $('#map').find('.leaflet-marker-icon').length.should.be.exactly(1); // basic check to see if markers are rendered

            done();

        });

    it('should render multiple choice widget',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "multiple_choice",
                logic: {},
                answer: [],
                choices: [],
                question_title: "Seriously, I'm gonna go back and check out all the noms",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("Seriously, I'm gonna go back and check out all the noms");
            
            $('.content')
                .find('select')
                .select()
                .val()
                .should.match("null"); //TODO: why was the base option set to the string null

            should($('.content')
                .find('select')
                .attr('multiple')).not.be.ok

            done();

        });

    it('should render multiple choice widget with other',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "multiple_choice",
                logic: {with_other: true},
                answer: [{response: "other is selected since choices len = 0"}],
                choices: [],
                question_title: "Seriously, I'm gonna go back and check out all the noms+",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("Seriously, I'm gonna go back and check out all the noms+");

            $('.content')
                .find('select')
                .select()
                .val()
                .should.match("other");

            $('.content')
                .find('input')
                .val()
                .should.match(question.answer[0].response);

            done();

        });

    it('should render multiple choice with allow multiple',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "multiple_choice",
                logic: {},
                allow_multiple: true,
                answer: [],
                choices: [],
                question_title: "NPH is a cool dude",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            Widgets[question.type_constraint_name](question, $('.content'));

            $('.question__title')
                .text()
                .should.match("NPH is a cool dude");
            
            $('.content')
                .find('select')
                .attr('multiple')
                .should.match("multiple");

            done();

        });
});

