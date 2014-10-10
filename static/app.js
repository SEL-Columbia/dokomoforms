(function() {


App = function(survey) {
    Survey.id = survey.survey_id;
    Survey.questions = survey.questions;
    Survey.questions.unshift({
        title: "What's your location?",
        id: 'no_id_yet',
        type_constraint_name: 'location'
    });
    Survey.events();
    Survey.render(0);
    
    window.applicationCache.addEventListener('updateready', function() {
        alert('app updated, reloading...');
        window.location.reload();
    });
};

var Survey = {
    id: null,
    questions: []
};

Survey.events = function() {
    var self = this;
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? -1 : 1;
        var index = $('.survey').data('index') + offset;
        if (index >= 0 && index <= self.questions.length) {
            self.render(index);
        }
        return false;
    });
};

Survey.render = function(index) {
    var question = this.questions[index];
    var survey = $('.survey');
    
    if (question) {
        // Show widget
        var templateHTML = $('#widget_' + question.type_constraint_name).html();
        var template = _.template(templateHTML);
        var html = template({question: question});
        
        // Render question
        survey.empty()
            .data('index', index)
            .html(html);
        
        // Attach widget events
        Widgets[question.type_constraint_name](question, survey);
    } else {
        // Show submit page
        survey.empty()
            .data('index', index)
            .html($('#template_submit').html())
            .find('.question__btn')
            .click(this.submit);
    }
    
    // Update nav
    $('.page_nav__progress')
        .text((index + 1) + ' / ' + (this.questions.length + 1));
};

Survey.submit = function() {
    var self = Survey;
    var data = {
        survey_id: self.id,
        answers: self.questions
    };
    console.log(data);
    $.post('', data, function() {
        console.log('done');
    });
};


var Widgets = {};
Widgets.text = function(question, survey) {
    // This widget's events. Called after survey template rendering.
    // Responsible for setting the question object's answer
    //
    // question: question data
    // survey: survey container, DOM element
    $(survey)
        .find('input')
        .on('keyup', function() {
            question.answer = this.value;
        });
};

Widgets.integer = function(question, survey) {
    $(survey)
        .find('input')
        .keyup(function() {
            question.answer = parseInt(this.value);
        });
};

Widgets.location = function(question, survey) {
    // TODO: add location status
    
    var input = $(survey)
        .find('input')
        .keydown(function() {
            return false;
        });
    
    $(survey)
        .find('.question__btn')
        .click(function() {
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    var coords = position.coords;
                    question.answer = coords;
                    input.val(coords.latitude + ', ' + coords.longitude);
                }, function error() {
                    alert('error')
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });
};



    
})();