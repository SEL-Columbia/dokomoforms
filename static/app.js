

App = {
    unsynced: [] // unsynced surveys
};
App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, survey.questions);
    
    $('.nav__sync')
        .click(function() {
            App.sync();
        });
        
        
    // Syncing intervals
    setInterval(function() {
        if (navigator.onLine && self.unsynced.length) {
            _.each(self.unsynced, function(survey) {
                survey.submit();
            });
        }
    }, 10000);
    
    // AppCache updates
    window.applicationCache.addEventListener('updateready', function() {
        alert('app updated, reloading...');
        window.location.reload();
    });
};


function Survey(id, questions) {
    var self = this;
    this.id = id;
    this.questions = questions;
    
    // Load answers from localStorage
    var answers = JSON.parse(localStorage[this.id] || '{}');
    this.questions.forEach(function(question) {
        question.answer = answers[question.question_id] || null;
    });
    
    // Page navigation
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? -1 : 1;
        var index = $('.content').data('index') + offset;
        if (index >= 0 && index <= self.questions.length) {
            self.render(index);
        }
        return false;
    });
    
    // Render first question
    this.render(0);
};

Survey.prototype.render = function(index) {
    var self = this;
    var question = this.questions[index];
    var content = $('.content');
    
    if (question) {
        // Show widget
        var templateHTML = $('#widget_' + question.type_constraint_name).html();
        var template = _.template(templateHTML);
        var html = template({question: question});
        
        // Render question
        content.empty()
            .data('index', index)
            .html(html);
        
        // Attach widget events
        Widgets[question.type_constraint_name](question, content);
    } else {
        // Show submit page
        content.empty()
            .data('index', index)
            .html($('#template_submit').html())
            .find('.question__btn')
                .click(function() {
                    self.submit();
                });
    }
    
    // Update nav
    $('.page_nav__progress')
        .text((index + 1) + ' / ' + (this.questions.length + 1));
};

Survey.prototype.submit = function() {
    var self = this;
    var sync = $('.nav__sync')[0];
    var save_btn = $('.question__saving')[0];
    var answers = {};
    
    // Fetch answers
    _.each(self.questions, function(question) {
        answers[question.question_id] = question.answer;
    });
    
    // Save a copy locally
    localStorage[self.id] = JSON.stringify(answers);

    var data = {
        survey_id: self.id,
        answers: self.questions
    };
    
    sync.classList.add('icon--spin');
    save_btn.classList.add('icon--spin');
    
    $.post('', {data: JSON.stringify(data)})
        .success(function() {
            console.log('Survey submitted successfully.');
        })
        .fail(function() {
            console.log('Submission failed, will try again later.');
            App.unsynced.push(self);
        })
        .done(function() {
            setTimeout(function() {
                sync.classList.remove('icon--spin');
                save_btn.classList.remove('icon--spin');
            }, 1000);
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



    
