var NEXT = 1;
var PREV = -1;

var Widgets = require('./widgets.js').Widgets;

//XXX TODO: remove reference to Widgets
function Survey(id, version, questions, metadata, title, created_on, last_updated) {
    var self = this;
    this.id = id;
    this.questions = questions;
    this.metadata = metadata;
    this.author = metadata.author || 'anon';
    this.org = metadata.organization || 'independant';
    this.version = version;
    this.title = title;
    this.created_on = new Date(created_on).toDateString();
    this.last_updated = new Date(last_updated).toDateString();

    // Load answers from localStorage
    var answers = JSON.parse(localStorage[this.id] || '{}');
    //console/g.log(answers);
    _.each(self.questions, function(question) {
        question.answer = answers[question.question_id] || [];
        // Set next pointers
        question.next = self.getQuestion(question.question_to_sequence_number);
    });

    App.location = answers['location'] || {};

    // Know where to start, and number
    self.current_question = self.questions[0];
    self.lowest_sequence_number = self.current_question.sequence_number;
    self.first_question = self.current_question;

    // Now that you know order, you can set prev pointers
    var curr_q = self.current_question;
    var prev_q = null;
    do {
        curr_q.prev = prev_q;
        prev_q = curr_q;
        curr_q = curr_q.next;
    } while (curr_q);
    
}

// Search by sequence number instead of array pos
Survey.prototype.getQuestion = function(seq) {
    var self = this;
    for(var i = 0; i < self.questions.length; i++) {
        if (self.questions[i].sequence_number === seq) {
            return self.questions[i];
        }
    }

    return null;
};

// Answer array may have elements even if answer[0] is undefined
// Return a non empty response or an empty one if none found
Survey.prototype.getFirstResponse = function(question) {
    for (var i = 0; i < question.answer.length; i++) {
        var answer = question.answer[i];
        if (answer && typeof answer.response !== 'undefined') {
            return answer
        }
    }

    return {'response': null, 'is_type_exception': false, 'metadata': null};
};

// Choose next question, deals with branching and back/forth movement
Survey.prototype.next = function(offset) {
    var self = this;

    var next_question = offset === PREV ? this.current_question.prev : this.current_question.next;
    var index = $('.content').data('index');

    var first_answer = this.getFirstResponse(this.current_question); 
    var first_response = first_answer.response;
    var first_is_type_exception = first_answer.is_type_exception;
    var first_metadata = first_answer.metadata;

    // Backward at first question
    if (index === self.lowest_sequence_number && offset === PREV) {
        App.splash();
        return;
    }

    // Backwards at submit page
    if (index === this.questions.length + 1 && offset === PREV) {
        // Going backwards at submit means render ME;
        next_question = this.current_question;
    } 
    
    // Normal forward
    if (offset === NEXT) {
        // Is it a valid response?
        bad_answers = [];
        this.current_question.answer.forEach(function(resp) {
            if (resp && resp.failed_validation)
                bad_answers.push(resp);
        });

        if (bad_answers.length) {
            App.message(bad_answers.length 
            + ' response(s) found not valid for question type: ' 
            + self.current_question.type_constraint_name, 'Survey Response Error', 'message-error');
            return;
        }

        // Are you required?
        if (this.current_question.logic.required && (first_response === null)) {
            App.message('Survey requires this question to be completed.','Survey Required Response',  'message-error');
            return;
        }

        // Is the only response and empty is other response?
        if (first_is_type_exception && !first_response) {
            App.message('Please provide a reason before moving on.', 'Survey Missing Reason', 'message-error');
            return;
        }

        // Check if question was a branching question
        if (this.current_question.branches && (first_response !== null)) {
            var branches = this.current_question.branches;
            for (var i=0; i < branches.length; i++) {
                if (branches[i].question_choice_id === first_response) {
                    next_question = self.getQuestion(branches[i].to_sequence_number);
                    // update pointers
                    self.current_question.next = next_question;
                    next_question.prev = self.current_question; 
                    break; // only one set of ptrs ever needed updating
                }
            }
        }
    }

    self.saveState();
    self.render(next_question);
};

// Render template for given question
Survey.prototype.render = function(question) {
    $('header').removeClass('title-extended');
    $('.title_menu').hide();

    var self = this;
    $('.overlay').hide(); // Always remove overlay after moving

    // Clear any interval events
    if (Widgets.interval) {
        window.clearInterval(Widgets.interval);
        Widgets.interval = null;
    }

    var index = question ? question.sequence_number : this.questions.length + 1;

    // Update navs
    var barnav  = $('.bar-nav');
    var barnavHTML = $('#template_nav').html();
    var barnavTemplate = _.template(barnavHTML);
    var compiledHTML = barnavTemplate({
        'index': index,
        'total': this.questions.length + 1,
    });

    barnav.empty()
        .html(compiledHTML);

    // Update footer
    var barfoot = $('.bar-footer');
    var barfootHTML;
    var barfootTemplate;

    barfoot.removeClass('bar-footer-extended');
    barfoot.removeClass('bar-footer-super-extended');
    barfoot.css("height", "");

    // Update content
    var content = $('.content');
    var widgetHTML;
    var widgetTemplate;
    
    if (question) {

        // Add the next button
        barfootHTML = $('#template_footer').html();
        barfootTemplate = _.template(barfootHTML);
        compiledHTML = barfootTemplate({
            'other_text': question.logic.other_text
        });

        barfoot.empty()
            .html(compiledHTML);

        // Show widget
        widgetHTML = $('#widget_' + question.type_constraint_name).html();
        widgetTemplate = _.template(widgetHTML);
        compiledHTML = widgetTemplate({question: question});
        self.current_question = question;

        // Render question
        content.removeClass('content-shrunk');
        content.removeClass('content-super-shrunk');
        content.empty()
            .data('index', index)
            .html(compiledHTML)
            .scrollTop(); //XXX: Ignored in chrome ...
        
        // Attach widget events
        Widgets[question.type_constraint_name](question, content, barfoot);

    } else {
        // Add submit button
        barfootHTML = $('#template_footer__submit').html();
        barfootTemplate = _.template(barfootHTML);
        compiledHTML = barfootTemplate({
        });

        barfoot.empty()
            .html(compiledHTML)
            .find('.submit_btn')
                .one('click', function() {
                    self.submit();
                });

        // Show submit page
        widgetHTML = $('#template_submit').html();
        widgetTemplate = _.template(widgetHTML);
        compiledHTML = widgetTemplate({
                'name': App.submitter_name,
                'email': App.submitter_email
        });

        // Render submit page
        content.removeClass('content-shrunk');
        content.removeClass('content-super-shrunk');
        content.empty()
            .data('index', index)
            .html(compiledHTML)
            .find('.name_input')
            .keyup(function() {
                App.submitter_name = this.value;
                localStorage.name = App.submitter_name;
            });

        content
            .find('.email_input')
            .keyup(function() {
                App.submitter_email = this.value;
                localStorage.email = App.submitter_email;
            });
    }
    
    // Update nav
    $('.page_nav__progress')
        .text((index) + ' / ' + (this.questions.length + 1));
    
    // Page navigation
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = $(this).hasClass('page_nav__prev') ? PREV : NEXT;
        self.next(offset);
    });
    

};

Survey.prototype.saveState = function() {
    var self = this;
    var answers = {};

    // Save answers locally 
    _.each(self.questions, function(question) {
        answers[question.question_id] = question.answer;
    });
    answers['location'] = App.location;

    // Save answers in storage
    localStorage[self.id] = JSON.stringify(answers);
}

Survey.prototype.clearState = function() {
    var self = this;

    // Clear answers locally 
    _.each(self.questions, function(question) {
        question.answer = [];
    });
    App.location = {};

    // Clear answers in storage
    localStorage[self.id] = JSON.stringify({});
}

Survey.prototype.submit = function() {
    var self = this;

    // Prepare POST request
    var survey_answers = [];
    self.questions.forEach(function(q) {
        //console.log('q', q);
        q.answer.forEach(function(ans, ind) {

            if (ans == null) {
                return;
            }

            var response =  ans.response;
            var is_type_exception = ans.is_type_exception || false;
            var metadata = ans.metadata || {};
            var is_new_facility = metadata.is_new; //XXX: Should I remove this is new marking?

            if (response == null) { 
                return;
            }

            if (is_new_facility) {
                // Record this new facility for Revisit s)ubmission
                App.unsynced_facilities[response.id] = {
                    'name': metadata.name, 'uuid': response.id, 
                    'properties' : {'sector': metadata.sector},
                    'coordinates' : [response.lon, response.lat]
                };

                // Store it in facilities as well
                App.facilities[response.id] = App.unsynced_facilities[response.id];
            }

            survey_answers.push({
                question_id: q.question_id,
                answer: response,
                answer_metadata: metadata,
                is_type_exception: is_type_exception
            });

        });
    });

    var data = {
        submitter: App.submitter_name || "anon",
        submitter_email: App.submitter_email || "anon@anon.org",
        survey_id: self.id,
        answers: survey_answers,
        save_time: new Date().toISOString()
    };

    console.log('saved submission:', data);
    
    // Don't post with no replies
    if (JSON.stringify(survey_answers) === '[]') {
      // Not doing instantly to make it seem like App tried reaaall hard
      setTimeout(function() {
            App.message('Saving failed, No questions answered in Survey!', 'Survey Empty Submission', 'message-warning');
            App.splash();
      }, 1000);
      return;
    } 

    // Save Revisit data 
    localStorage.setItem("facilities", 
            JSON.stringify(App.facilities));

    localStorage.setItem("unsynced_facilities", 
            JSON.stringify(App.unsynced_facilities));
    
    // Clear State
    self.clearState();

    // Save Submission data
    App.unsynced.push(data);
    var unsynced = JSON.parse(localStorage.unsynced); 
    unsynced[self.id] = App.unsynced;
    localStorage['unsynced'] = JSON.stringify(unsynced);
    //App.message('Please remember to sync submissions when connected to the internet.', 'Survey Saved', 'message-primary');
    App.splash();


};

exports.Survey = Survey;
