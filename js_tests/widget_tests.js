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

var mah_code = require('../dokomoforms/static/bundle.js');
var Widgets = mah_code.Widgets;
var App = mah_code.App;


// Location and Facility Question rendering
describe('Widget creation tests', function(done) {
    before(function(done) {
        done();
    });


    beforeEach(function(done) {
        $.mockjax.clear();
        App.facilities = [];
        App.unsynced_facilities = {};
        App.location = {};
        done();
    });

    afterEach(function(done) {
        $.mockjax.clear();
        $(".page_nav__next").off('click'); //XXX Find out why events are cached
        $(".page_nav__prev").off('click');
        $('.content').empty();
        $('.bar-footer').empty()
        localStorage = {};
        App.location = {};
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
                .length.should.equal(1); // Removal is always present

            done();

    });
    
    it('should render widget with dont-know button but no displayed other input and active regular inputs',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {allow_dont_know: true},
                allow_multiple: true,
                question_title: "Whiplash was real good dont-know",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

            $('.bar-footer')
                .find('.question__btn__other')
                .length.should.equal(1); // Should be there AND visible (its always there)

            $('.bar-footer')
                .find('.question__btn__other')
                [0].style.display.should.equal(''); // Should be there AND visible (its always there)

            // Isn't active if no other_response was picked
            var other_div = $('.question__dont_know');
            other_div.length.should.equal(1);
            other_div[0].style.display.should.equal('none');

            // Regular input is active
            $('.text_input')[0].disabled.should.equal(false);

            done();

    });

    it('should render widget with dont-know button but AND displayed other input and INACTIVE regular inputs',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {allow_dont_know: true},
                allow_multiple: true,
                question_title: "Whiplash was real good otttherr",
                answer: [{response: 'good times', is_type_exception: true, metadata: { 'type_exception': 'dont_know' }}, 
                    {response: 1111, is_type_exception: false }], // can never happen (having two types of responses) in frontend 
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});


            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

            $('.bar-footer')
                .find('.question__btn__other')
                .length.should.equal(1); // Should be there AND visible (its always there)

            $('.bar-footer')
                .find('.question__btn__other')
                [0].style.display.should.equal(''); // Should be there AND visible (its always there)

            //  Is active with correct response
            var other_div = $('.question__dont_know');
            other_div.length.should.equal(1);
            other_div[0].style.display.should.equal('');
            $('.dont_know_input').val().should.equal('good times');


            // Regular input is INACTIVE
            $('.text_input')[0].disabled.should.equal(true);

            // Response is cleaned up
            question.answer.should.match([{response: 'good times', is_type_exception: true, metadata: { 'type_exception': 'dont_know' }}]); 
            done();
    });

    it('should render widget with dont-know button but AND NO displayed other input and ACTIVE regular inputs' 
            + ' when theres just a regular response and some out of order other response',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "decimal",
                logic: {allow_dont_know: true},
                allow_multiple: true,
                question_title: "Whiplash was real good otttherr",
                answer: [{response: 777, is_type_exception: false}],
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});
            
            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

            $('.bar-footer')
                .find('.question__btn__other')
                .length.should.equal(1); // Should be there AND visible (its always there)

            $('.bar-footer')
                .find('.question__btn__other')
                [0].style.display.should.equal(''); // Should be there AND visible (its always there)

            //  Is inactive with no response
            var other_div = $('.question__dont_know');
            other_div.length.should.equal(1);
            other_div[0].style.display.should.equal('none');
            $('.dont_know_input').val().should.equal('');

            // Regular input is ACTIVE
            $('.text_input').not('.other_input')[0].disabled.should.equal(false);
            $('.text_input').not('.other_input').val().should.equal('777');

            // Response is cleaned up
            question.answer.should.match([{response: 777, is_type_exception: false }]);

            done();
    });

    it('should render widget with NO dont-know button but AND NO displayed other input and ACTIVE regular inputs', 
    function(done) {
        var question = {
            question_to_sequence_number: -1,
            type_constraint_name: "decimal",
            logic: {allow_dont_know: false},
            allow_multiple: true,
            question_title: "Whiplash was real good otttherr",
            sequence_number: 1
        };
        
        // Create content div with widget template
        var widgetHTML = $('#widget_' + question.type_constraint_name).html();
        var widgetTemplate = _.template(widgetHTML);
        var compiledHTML = widgetTemplate({question: question, start_loc: {'lat': 40, 'lon': 70}});
        
        $('.content')
            .data('index', 1)
            .html(compiledHTML)

        var barfootHTML = $('#template_footer').html();
        var barfootTemplate = _.template(barfootHTML);
        compiledHTML = barfootTemplate({
            'other_text': question.logic.other_text
        });

        $('.bar-footer').html(compiledHTML);
        $('.bar-footer').removeClass('bar-footer-extended');
        $('.bar-footer').removeClass('bar-footer-super-extended');
        $('.bar-footer').css("height", "");

        Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

        $('.bar-footer')
            .find('.question__btn__other')
            .length.should.equal(1); // there but hidden
        $('.bar-footer')
            .find('.question__btn__other')
            [0].style.display.should.equal('none');

        // Div not added 
        var other_div = $('.question__dont_know');
        other_div.length.should.equal(0);

        // Regular input is ACTIVE
        $('.text_input').not('.other_input')[0].disabled.should.equal(false);

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

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

            $('.text_input')
                .not('.other_input')
                .val()
                .split(" ")[1]
                .should.match("5");
            
            $('.text_input')
                .not('.other_input')
                .val()
                .split(" ")[0]
                .should.match("7");


            $('.question__title')
                .text()
                .should.match("Birdman was meh, clearly appealed to the judges though");

            $('#map').find('.leaflet-marker-icon').length.should.be.exactly(0);
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
            App.location =  {'lat': 40, 'lon': 70};

            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

            $('.question__title')
                .text()
                .should.match("Good year for flixs though+");


            $('.question__radio').length.should.match(10);
            done();

        });

    it('should render facility widget with unset location and no facilities',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "facility",
                logic: {},
                answer: [],
                question_title: "That lego movie song sucks",
                sequence_number: 1
            };
            
            // Create content div with widget template
            var widgetHTML = $('#widget_' + question.type_constraint_name).html();
            var widgetTemplate = _.template(widgetHTML);
            var compiledHTML = widgetTemplate({question: question});

            $('.content')
                .data('index', 1)
                .html(compiledHTML)

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

            $('.question__title')
                .text()
                .should.match("That lego movie song sucks");

            $('.question__radio').length.should.match(0);
            $('.facility__btn')[0].style.display.should.equal('none'); // Should be there but not visible
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

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

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
                logic: {allow_other: true},
                answer: [{response: "other is selected since choices len = 0", is_type_exception: true, metadata: {'type_exception' : 'other'}}],
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

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

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

            var barfootHTML = $('#template_footer').html();
            var barfootTemplate = _.template(barfootHTML);
            compiledHTML = barfootTemplate({
                'other_text': question.logic.other_text
            });

            $('.bar-footer').html(compiledHTML);
            $('.bar-footer').removeClass('bar-footer-extended');
            $('.bar-footer').removeClass('bar-footer-super-extended');
            $('.bar-footer').css("height", "");

            Widgets[question.type_constraint_name](question, $('.content'), $('.bar-footer'))

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

describe('Widget validate tests', function(done) {
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

    it('should validate lat lon questions passed in as "lat lon" correctly',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "location",
                logic: {},
                allow_multiple: true,
                answer: [],
                choices: [],
                question_title: "loco",
                sequence_number: 1
            };
            
            
            var response = Widgets._validate(question.type_constraint_name, "40.1 70.1");
            response.should.match({'lat': 40.1, 'lon': 70.1});
            done();

        });
    
    it('should validate lat lon questions passed in as "lat " correctly as invalid',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "location",
                logic: {},
                allow_multiple: true,
                answer: [],
                choices: [],
                question_title: "loco",
                sequence_number: 1
            };
            
            
            var response = Widgets._validate(question.type_constraint_name, "40.1 ");
            should(response).match(null);
            done();

        });
    
    it('should validate lat lon questions passed in as " " correctly as invalid',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "location",
                logic: {},
                allow_multiple: true,
                answer: [],
                choices: [],
                question_title: "loco",
                sequence_number: 1
            };
            
            
            var response = Widgets._validate(question.type_constraint_name, " ");
            should(response).match(null);

            var response = Widgets._validate(question.type_constraint_name, "");
            should(response).match(null);
            done();

        });
    
    it('should validate lat lon questions passed in as "poop 40.1" correctly as invalid',
        function(done) {
            var question = {
                question_to_sequence_number: -1,
                type_constraint_name: "location",
                logic: {},
                allow_multiple: true,
                answer: [],
                choices: [],
                question_title: "loco",
                sequence_number: 1
            };
            
            
            var response = Widgets._validate(question.type_constraint_name, "poop 40.1");
            should(response).match(null);
            done();

        });
});
