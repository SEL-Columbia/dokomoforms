

App = {};
App.init = function(survey) {
    this.survey = new Survey(survey.survey_id, survey.questions);
    
    $('.nav__sync')
        .click(function() {
            App.sync();
        });
    
    window.applicationCache.addEventListener('updateready', function() {
        alert('app updated, reloading...');
        window.location.reload();
    });
};

App.sync = function() {
    var sync = $('.nav__sync')[0];
    var data = {
        survey_id: this.survey.id,
        answers: this.survey.questions
    };
    console.log(data);
    
    sync.classList.add('nav__sync--syncing');
    
    $.post('', {data: JSON.stringify(data)}, function() {
            console.log('done');
        })
        .fail(function() {
            alert('Update failed, please try syncing later');
        })
        .done(function() {
            setTimeout(function() {
                sync.classList.remove('nav__sync--syncing');
            }, 1000);
        });
};


function Survey(id, questions) {
    var self = this;
    this.id = id;
    this.questions = questions;
    
    var answers = JSON.parse(localStorage[this.id] || '{}');
    this.questions.forEach(function(question) {
        question.answer = answers[question.question_id] || null;
    });
    
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? -1 : 1;
        var index = $('.survey').data('index') + offset;
        if (index >= 0 && index <= self.questions.length) {
            self.render(index);
        }
        return false;
    });
    
    this.render(0);
};

Survey.prototype.render = function(index) {
    var self = this;
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
                .click(function() {
                    var answers = {};
                    self.questions.forEach(function(question) {
                        answers[question.question_id] = question.answer;
                    });
                    localStorage[self.id] = JSON.stringify(answers);
                    App.sync();
                });
    }
    
    // Update nav
    $('.page_nav__progress')
        .text((index + 1) + ' / ' + (this.questions.length + 1));
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



    
