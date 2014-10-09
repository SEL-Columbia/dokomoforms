(function() {


App = function(survey) {
    Page.questions = survey.questions;
    Page.events();
    Page.render(0);
};

var Page = {
    questions: []
};

Page.events = function() {
    var self = this;
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? -1 : 1;
        var index = $('.page').data('index') + offset;
        if (index >= 0 && index < self.questions.length) {
            self.render(index);
        }
        return false;
    });
};

Page.render = function(index) {
    var question = this.questions[index];
    var templateHTML = $('#widget_' + question.type_constraint_name).html();
    var template = _.template(templateHTML);
    var html = template({question: question});
    
    // Render question
    var page = $('.page')
        .empty()
        .data('index', index)
        .html(html);
    
    // Attach widget events
    Widgets[question.type_constraint_name](question, page);
    
    // Update nav
    $('.page_nav__progress')
        .text((index + 1) + ' / ' + this.questions.length);
};


var Widgets = {};
Widgets.text = function(question, page) {
    // This widget's events. Called after page template rendering.
    // Responsible for setting the question object's answer
    //
    // question: question data
    // page: page container, DOM element
    $(page)
        .find('input')
        .on('keyup', function() {
            question.answer = this.value;
        });
};

Widgets.integer = function(question, page) {
    $(page)
        .find('input')
        .keyup(function() {
            question.answer = parseInt(this.value);
        });
};

Widgets.location = function(question, page) {
    // TODO: add location status
    
    var input = $(page)
        .find('input')
        .keydown(function() {
            return false;
        });
    
    $(page)
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