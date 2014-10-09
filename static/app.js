(function() {


App = function(questions) {
    Page.events();
    Page.render(0);
};

var Page = {
    questions: [
        {
            id: 'facility_name',
            label: 'Health facility name',
            type: 'text'
        },
        {
            id: 'facility_location',
            label: 'Facility location',
            type: 'location'
        },
        {
            id: 'bed_capacity',
            label: 'Bed Capacity?',
            type: 'number',
            min: 0
        },
        {
            id: 'suspected_cases',
            label: 'Number of suspected Ebola cases',
            type: 'number',
            min: 0
        },
        {
            id: 'confirmed_cases',
            label: 'Number of confirmed Ebola cases',
            type: 'number',
            min: 0
        },
        {
            id: 'confirmed_deaths',
            label: 'Number of confirmed Ebola deaths',
            type: 'number',
            min: 0
        },
        {
            id: 'recovered_cases',
            label: 'Number of recovered and released Ebola cases',
            type: 'number',
            min: 0
        },
        {
            id: 'litres_bleach',
            label: 'Liters of bleach',
            type: 'number',
            min: 0
        },
        {
            id: 'num_gloves',
            label: 'Number of gloves',
            type: 'number',
            min: 0
        },
        {
            id: 'face_shields',
            label: 'Number of face shields',
            type: 'number',
            min: 0
        },
        {
            id: 'num_respirators',
            label: 'Number of N95 respirators',
            type: 'number',
            min: 0
        },
        {
            id: 'num_goggles',
            label: 'Number of goggles',
            type: 'number',
            min: 0
        }
    ]
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
    var template = _.template('#widget_' + question.type);
    var html = template({question: question});
    
    // Render question
    $('.page')
        .empty()
        .data('index', index)
        .html(html);
    
    // Attach widget events
    Widgets[question.type]();
    
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

Widgets.number = function(question, page) {
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
        .find('question__btn')
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