var NEXT = 1;
var PREV = -1;

var Widgets = require('./widgets.js').Widgets;

/*
 * Create a new Survey
 *
 * @id: survey id
 * @version: current survey version
 * @questions: survey questions
 * @metadata: JSON representing misc survey details
 * @title: survey title
 * @created_on: ISO 8601 time representing survey creation time
 * @last_update_time: ISO 8601 time representing survey last_update_time time
 */
function Survey(id, version, questions, answers, metadata, title, created_on, last_update_time, default_language) {
    var self = this;
    this.id = id;
    this.questions = questions;
    this.metadata = metadata;
    this.author = 'anon'; //XXX 
    this.org = 'independant'; //XXX
    this.version = version;
    this.title = title;
    this.created_on = new Date(created_on).toDateString();
    this.last_update_time = new Date(last_update_time).toDateString();
    this.default_language = default_language;
    console.log(self.default_language);

    // Set up questions
    _.each(self.questions, function(question, idx) {
        question.answer = answers[question.id] || [];
        question.default_language = self.default_language;
        // Set next and prev pointers
        if (idx > 0)
            question.prev = self.questions[idx - 1];
        if (idx < self.questions.length - 1)
            question.next = self.questions[idx + 1];

    });


    // Know where to start, and number
    self.current_question = self.questions[0];
    self.first_question = self.current_question;

    // Now that you know order, you can set prev pointers
    var curr_q = self.current_question;
    var prev_q = null;
    counter  = 1;
    do {
        console.log("hey");
        counter++;
        curr_q.prev = prev_q;
        prev_q = curr_q;
        curr_q = curr_q.next;
    } while (curr_q && counter < 20);
    
}

/*
 * Search for a survey question by id
 * @id: Question id
 *
 * Returns a question object
 */
Survey.prototype.getQuestion = function(id) {
    var self = this;
    for(var i = 0; i < self.questions.length; i++) {
        // XXX search nested structure by current level only
        if (self.questions[i].id === id) {
            return self.questions[i];
        }
    }

    return null;
};

/*
 * Return first response found in given question, 
 * return an empty response otherwise.
 *
 * @question: Survey question object
 *
 * Returns a JSON response
 */
Survey.prototype.getFirstResponse = function(question) {
    for (var i = 0; i < question.answer.length; i++) {
        var answer = question.answer[i];
        if (answer && typeof answer.response !== 'undefined') {
            return answer
        }
    }

    return {'response': null, 'is_type_exception': false, 'metadata': null};
};

/*
 * Choose the next question to render. Calls survey.render
 * Deals with branching and back/forth movement.
 * 
 * @offset: either NEXT or PREV
 */
Survey.prototype.next = function(offset) {
    var self = this;

    var next_question = offset === PREV ? this.current_question.prev : this.current_question.next;
    var index = $('.content').data('index');

    // Backward at first question
    if (index === 1 && offset === PREV) {
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
        var first_answer = this.getFirstResponse(this.current_question); 
        var first_response = first_answer.response;
        var first_is_type_exception = first_answer.is_type_exception;
        var first_metadata = first_answer.metadata;


        // Are all responses valid?
        bad_answers = [];
        this.current_question.answer.forEach(function(resp) {
            if (resp && resp.failed_validation)
                bad_answers.push(resp);
        });

        if (bad_answers.length) {
            App.message(bad_answers.length 
            + ' response(s) found not valid for question type: ' 
            + self.current_question.type_constraint, 'Survey Response Error', 'message-error');
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
                    next_question = self.getQuestion(branches[i].to_question_id);
                    // update pointers
                    self.current_question.next = next_question;
                    next_question.prev = self.current_question; 
                    break; // only one set of ptrs ever needed updating
                }
            }
        }
    }

    App.saveState();
    self.render(next_question);
};

/*
 * Render template for given question.
 * Render save page if question object is null.
 *
 * @question: A survey question object
 */
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

    // Determine index
    var index = question ? self.questions.indexOf(question) + 1: this.questions.length + 1;

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
        widgetHTML = $('#widget_' + question.type_constraint).html();
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
        Widgets[question.type_constraint](question, content, barfoot);

        
    } else { //XXX Move all of this
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
    
    // Update current question number
    $('.page_nav__progress')
        .text((index) + ' / ' + (this.questions.length + 1));
    
    // Page navigation
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = $(this).hasClass('page_nav__prev') ? PREV : NEXT;
        self.next(offset);
    });
    
};

/*
 * Get the current state of the survey (i.e question answers).
 */
Survey.prototype.getState = function() {
    var self = this;
    var answers = {};

    // Save answers locally 
    _.each(self.questions, function(question) {
        answers[question.id] = question.answer;
    });

    answers['location'] = App.location;

    return answers;
}

/*
 * Clear the current state of the survey (i.e question answers).
 */
Survey.prototype.clearState = function() {
    var self = this;

    // Clear answers locally 
    _.each(self.questions, function(question) {
        question.answer = [];
    });
}

/*
 * 'Submit' survey to localStorage and App.unsynced array after transforming 
 * survey to Dokomoforms submission API form.
 */
Survey.prototype.submit = function() {
    var self = this;

    // Prepare POST request
    var survey_answers = [];
    self.questions.forEach(function(q) {
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
                id: q.id,
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

    // XXX Move everything below out of here
    // Save Revisit data 
    localStorage.setItem("facilities", 
            JSON.stringify(App.facilities));

    localStorage.setItem("unsynced_facilities", 
            JSON.stringify(App.unsynced_facilities));
    
    // Clear State
    App.clearState();

    // Save Submission data
    App.unsynced.push(data);
    var unsynced = JSON.parse(localStorage.unsynced); 
    unsynced[self.id] = App.unsynced;
    localStorage['unsynced'] = JSON.stringify(unsynced);
    //App.message('Please remember to sync submissions when connected to the internet.', 'Survey Saved', 'message-primary');
    App.splash();


};

exports.Survey = Survey;
