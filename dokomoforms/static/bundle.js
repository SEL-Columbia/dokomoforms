(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
//TODO:Remove reference to App

/*
 * Revisit get facilities API call. 
 *
 * @lat: latitude value
 * @lng: longitude value
 * @rad: radius in KM
 * @lim: number of facilities to return
 * @cb: Success callback
 */
function getNearbyFacilities(lat, lng, rad, lim, cb) {
    var url = "http://staging.revisit.global/api/v0/facilities.json"; 

    // Revisit ajax req
    $.get(url,{
            near: lat + "," + lng,
            rad: rad,
            limit: lim,
            //sortDesc: "updatedAt",
            fields: "name,uuid,coordinates,properties:sector", //filters results to include just those three fields,
        },
        function(data) {
            facilities = {};
            data.facilities.forEach(function(facility) {
                facilities[facility.uuid] = facility;
            });
            // Add in our unsynced ones as well
            Object.keys(App.unsynced_facilities).forEach(function(uuid) {
                facilities[uuid] = App.unsynced_facilities[uuid];
            });

            App.facilities = facilities;
            localStorage.setItem("facilities", JSON.stringify(facilities));
            if (cb) {
                cb(facilities); //drawFacillities callback probs
            }
        }
    );
}

/*
 * Revisit post facility API call. 
 *
 * @facility: facility object to post
 */
function postNewFacility(facility) {
    var url = "http://staging.revisit.global/api/v0/facilities.json"; 

    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(facility),
        processData: false,
        dataType: 'json',
        success: function() {
            //App.message('Facility Added!', 'message-primary');
            // If posted, we don't an unsynced reference to it anymore
            delete App.unsynced_facilities[facility.uuid];
        },
        
        headers: {
            "Authorization": "Basic " + btoa("dokomoforms" + ":" + "password")
                //DONT DO THIS XXX XXX
        },

        error: function() {
            //App.message('Facility submission failed, will try again later.', 'message-warning');
        },
        
        complete: function() {
            localStorage.setItem("facilities", 
                    JSON.stringify(App.facilities));

            localStorage.setItem("unsynced_facilities", 
                    JSON.stringify(App.unsynced_facilities));

        }
    });
}

/*
 * Generate objectID compatitable with Mongo for the Revisit API
 *
 * Returns an objectID string
 */
function objectID() {
    return 'xxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[x]/g, function() {
        var r = Math.random()*16|0;
        return r.toString(16);
    });
}

exports.getNearbyFacilities = getNearbyFacilities; 
exports.postNewFacility = postNewFacility;
exports.objectID = objectID;


},{}],2:[function(require,module,exports){
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

    return {'response': null, 'metadata': {}};
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
        var first_is_type_exception = Boolean(first_answer.metadata.type_exception);


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
            var metadata = ans.metadata || {};
            var is_new_facility = metadata.is_new; //XXX: Should I remove this is new marking?

            if (response == null) { 
                return;
            }

            // Fill in metadata
            response.response_type = 'answer';
            if (metadata.type_exception) 
                response.response_type = response[metadata.type_exception];

            if (is_new_facility) {
                // Record this new facility for Revisit s)ubmission
                App.unsynced_facilities[response.id] = {
                    'name': response.facility_name, 'uuid': response.id, 
                    'properties' : {'sector': response.facility_sector},
                    'coordinates' : [response.lon, response.lat]
                };

                // Store it in facilities as well
                App.facilities[response.id] = App.unsynced_facilities[response.id];
            }

            survey_answers.push({
                survey_node_id: q.id,
                response: response,
                type_constraint: q.type_constraint
            });

        });
    });

    var data = {
        submitter_name: App.submitter_name || "anon",
        submitter_email: App.submitter_email || "anon@anon.org",
        submission_type: "unauthenticated", //XXX 
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

},{"./widgets.js":3}],3:[function(require,module,exports){
var ON = true;
var OFF = false;
var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

//TODO:Remove refernce to App
var getNearbyFacilities = require('./facilities.js').getNearbyFacilities;
var objectID = require('./facilities.js').objectID;

/*
 * Widgets for every question type. Called after page template rendering.
 * Responsible for setting the question object's answer and dealing with all 
 * user events.
 *
 * Underscore methods are helper methods that encapsulate functionality that can
 * appear on any question type.
 */
var Widgets = {
    interval: null,
};

/*
 * Generic widget event handler.
 *
 * All widgets store results in the questions.answer array
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 * @type: type of widget, handles all except
 *      multiple choice
 *      facility
 *      note
 */
Widgets._input = function(question, page, footer, type) {
    var self = this;
    
    // Render add/minus input buttons 
    self._renderRepeat(question, page, footer, type);

    //Render don't know
    self._renderDontKnow(question, page, footer, type);

    // Clean up answer array, short circuits on type_exception responses
    self._orderAnswerArray(question, page, footer, type);

    // Set up input event listner
    $(page)
        .find('.text_input')
        .keyup(function() { //XXX: Change isn't sensitive enough on safari?
            var ans_ind = $(page).find('input').index(this); 
            question.answer[ans_ind] = { 
                response: self._validate(type, this.value, question.logic),
                failed_validation: Boolean(null === self._validate(type, this.value, question.logic)),
                metadata: {},
            }
            // XXX Should i write the value back after validation?
        })
        .click(function() {
            $(page).animate({
                scrollTop: $(this).offset().top
            }, 500);
        });

    
};

/*
 * Handle creating multiple inputs for widgets that support it 
 *
 * @question: question data
 * @page: the widget container DOM element
 * @input: input field to base new input on
 */
Widgets._addNewInput = function(question, page, input) {
    if (question.allow_multiple) { //XXX: Technically this btn clickable => allow_multiple 
        input.parent()
            .clone(true)
            .insertAfter(input.parent())
            .find('input')
            .val(null)
            .focus();
    }
};

/*
 * Remove the input and specified index. 
 * Removes answer if input is the only input. 
 * Reorders answer array to keep answer array index in sync with DOM.
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element (orderAnswerArray requirement)
 * @type: question type name (XXX: Redundant with question object)
 * @inputs: current inputs on page array
 * @index: index inputs array for which input to remove
 */
Widgets._removeInput = function(question, page, footer, type, inputs, index) {
    var self = this;
    if (question.allow_multiple && (inputs.length > 1)) { //XXX: Technically this btn clickable => allow_multiple 
        delete question.answer[index];
        $(inputs[index]).parent().remove();
        self._orderAnswerArray(question, page, footer, type);
    } else {
        // atleast wipe the value
        delete question.answer[index];
        $(inputs[index]).val(null);

    }

    inputs
        .last()
        .focus()
};

/*
 * Recreates answer array to keep index values in sync with DOM input positions.
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element to search for dont_know responses
 * @type: question type name (XXX: Redundant with question object)
 */
Widgets._orderAnswerArray = function(question, page, footer, type) {
    question.answer = []; //XXX: Must be reinit'd to prevent sparse array problems
    var self = this;

    $(page).find('.text_input').each(function(i, child) { 
        if (child.value !== "") {
            question.answer[i] = {
                response: self._validate(type, child.value, question.logic),
                failed_validation: Boolean(null == self._validate(type, this.value, question.logic)),
                metadata: {}
            }
        }
    });

    $(footer).find('.dont_know_input').each(function(i, child) { 
        if (!child.disabled) {
            // if don't know input field has a response, break 
            question.answer = [{
                response: self._validate('text', child.value, question.logic),
                failed_validation: Boolean(null === self._validate('text', this.value, question.logic)),
                metadata: {
                    'type_exception': 'dont_know',
                },

            }];

            // there should only be one
            return false;
        }
    });
}

/*
 * Render 'don't know' section if question has with_other logic
 * Display response and alter widget state if first response is other
 *
 * @page: the widget container DOM element
 * @footer: footer container DOM element to search for dont_know responses
 * @type: question type name (XXX: Redundant with question object)
 * @question: question data
 */
Widgets._renderDontKnow = function(question, page, footer, type) {
    var self = this;
    // Render don't know feature 
    if (question.allow_dont_know) {
        $('.question__btn__other').show();
        footer.addClass('bar-footer-extended');
        page.addClass('content-shrunk');


        var repeatHTML = $('#template_dont_know').html();
        var widgetTemplate = _.template(repeatHTML);
        var compiledHTML = widgetTemplate({question: question});
        $(footer).append(compiledHTML);

        var other_response = question.answer 
            && question.answer[0] 
            && question.answer[0].metadata.type_exception === "dont_know";

        if (other_response) {
            $('.question__btn__other').find('input').prop('checked', true);
            this._toggleDontKnow(question, page, footer, type, ON);
        }

        // Clicking the dont-know checkbox handler
        $(footer)
            .find('.question__btn__other :checkbox')
            .change(function() { 
                var selected = $(this).is(':checked'); 
                self._toggleDontKnow(question, page, footer, type, selected);
            });


        // Set up other input event listener
        $(footer)
            .find('.dont_know_input')
            .keyup(function() { //XXX: Change isn't sensitive enough on safari?
                question.answer = [{ 
                    response: self._validate('text', this.value, question.logic),
                    failed_validation: Boolean(null === self._validate('text', this.value, question.logic)),
                    metadata: {
                        'type_exception': 'dont_know',
                    },
                }];
            });

        }
}

/*
 * Toggle the 'don't know' section based on passed in state value on given page
 * Alters question.answer array
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element to search for dont_know responses
 * @type: question type name (XXX: Redundant with question object)
 * @state: ON or OFF
 */
Widgets._toggleDontKnow = function(question, page, footer, type, state) {
    var self = this;
    question.answer = [];
    
    if (state === ON) {
        // Disable regular inputs
        $(page).find('input').each(function(i, child) { 
                $(child).attr('disabled', true);
        });
        
        // If select boxes are around, shut em down
        $(page).find('select').each(function(i, child) { 
                $(child).attr('disabled', true);
        });

        // hide em if he's around
        $(page).find('.other_input').hide();
        $(page).find('select').val('null');

        // Disable adder if its around
        $(page).find('.question__add').attr('disabled', true);

        // Toggle other input
        $(footer).find('.question__dont_know').show();
        $(footer).find('.dont_know_input').each(function(i, child) { 
            // Doesn't matter if response is there or not
            question.answer[0] = {
                response: self._validate('text', child.value, question.logic),
                failed_validation: Boolean(null === self._validate('text', this.value, question.logic)),
                metadata: {
                    'type_exception': 'dont_know',
                },
            }
        });

        // Bring div up
        page.addClass('content-super-shrunk');

        //Add overlay
        $('.overlay').fadeIn('fast');

        //footer.addClass('bar-footer-super-extended');
        footer.animate({height:220},200).addClass('bar-footer-super-extended');


        // Enable other input
        $(footer).find('.dont_know_input').each(function(i, child) { 
                $(child).attr('disabled', false);
        });

    } else if (state === OFF) { 
        // Enable regular inputs
        $(page).find('input').each(function(i, child) { 
              $(child).attr('disabled', false);
        });

        // Enable select input again
        $(page).find('select').each(function(i, child) { 
              $(child).attr('disabled', false);
        });

        // Enable adder if its around 
        $(page).find('.question__add').attr('disabled', false);

        // Toggle other inputs
        $(footer).find('.question__dont_know').hide();
        $(page).find('.text_input').each(function(i, child) { 
            if (child.value !== "") { 
                question.answer[i] = {
                    response: self._validate(type, child.value, question.logic),
                    failed_validation: Boolean(null === self._validate(type, this.value, question.logic)),
                    metadata: {},
                }
            }
        });
        
        // Hide overlay and shift div
        $('.overlay').fadeOut('fast');
        page.removeClass('content-super-shrunk');

        //footer.removeClass('bar-footer-super-extended');
        footer.animate({height:120},200).removeClass('bar-footer-super-extended');

        // Disable other input
        $(footer).find('.dont_know_input').each(function(i, child) { 
                $(child).attr('disabled', true);
        });
    }
}

/*
 * Render add button on given page. Set up add and remove input handlers.
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element to search for dont_know responses
 * @type: question type name (XXX: Redundant with question object)
 */
Widgets._renderRepeat = function(question, page, footer, type) {
    var self = this;
    // Render add/minus input buttons 
    if (question.allow_multiple) {
        var repeatHTML = $('#template_repeat').html();
        var widgetTemplate = _.template(repeatHTML);
        var compiledHTML = widgetTemplate({question: question});
        $(page).append(compiledHTML)

        // Click the + for new input
        $(page)
            .find('.question__add')
            .click(function() { 
                var input = $(page).find('.text_input').last();
                self._addNewInput(question, page, input);

            });

        // Click the - to remove that element
        $(page)
            .find('.question__minus')
            .click(function() { 
                var delete_icons = $(page).find('.question__minus');
                var inputs = $(page).find('.text_input');
                var index = delete_icons.index(this);
                self._removeInput(question, page, footer, type, inputs, index);
            });
    }
}

/* 
 * Basic input validation
 *
 * @type: question type name used to determine what validation to use
 * @answer: response to validate
 * @logic: JSON for question specific logic to enforce. (XXX USE THIS)
 */
Widgets._validate = function(type, answer, logic) {
    //XXX enforce logic
    var val = null;
    switch(type) {
        case "decimal":
            val = parseFloat(answer);
            if (isNaN(val)) {
                val = null;
            }
            break;
        case "integer":
            val = parseInt(answer);
            if (isNaN(val)) {
                val = null;
            }
            break;
        case "date":
            var resp = new Date(answer);
            var day = ("0" + resp.getDate()).slice(-2);
            var month = ("0" + (resp.getMonth() + 1)).slice(-2);
            var year = resp.getFullYear();
            val = year+"-"+(month)+"-"+(day);
            if(isNaN(year) || isNaN(month) || isNaN(day))  {
                val = null;
            }
            break;
        case "time":
              //XXX: validation for time
              if (answer) {
                  val = answer;
              }
              break;
        case "text":
              if (answer) {
                  val = answer;
              }
              break;
        case "location":
              if (answer && answer.split(" ").length == 2) {
                  var lat = parseFloat(answer.split(" ")[0]);
                  var lon = parseFloat(answer.split(" ")[1]);

                  if (!isNaN(lat) && !isNaN(lon)) {
                      val = {'lat': lat, 'lon': lon}
                  }
              }
              break;
        default:
              //XXX: Others aren't validated the same
              if (answer) {
                  val = answer;
              }
              break;
    }

    return val;
};

/* 
 * Text Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 */
Widgets.text = function(question, page, footer) {
    this._input(question, page, footer, "text");
};

/* 
 * Integer Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 */
Widgets.integer = function(question, page, footer) {
    this._input(question, page, footer, "integer");
};

/* 
 * Decimal Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 */
Widgets.decimal = function(question, page, footer) {
    this._input(question, page, footer, "decimal");
};

/* 
 * Date Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 */
Widgets.date = function(question, page, footer) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, footer, "date"); //XXX: Fix validation
};

/* 
 * Time and Timestamp Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 */
Widgets.time = function(question, page, footer) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, footer, "time"); //XXX: Fix validation
};

Widgets.timestamp = function(question, page, footer) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, footer, "timestamp"); //XXX: Fix validation
};

/* 
 * Note Widget
 */
Widgets.note = function() {
};

/* 
 * Multiple Choice Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 *
 * Multiple choice and multiple select are handled here.
 */
Widgets.multiple_choice = function(question, page, footer) {
    var self = this;

    // array of choice uuids
    var choices = [];
    question.choices.forEach(function(choice, ind) {
        choices[ind] = choice.choice_id;
    }); 
    choices[question.choices.length] = "other"; 


    //Render don't know
    self._renderDontKnow(question, page, footer, 'multiple_choice');

    // handle change for text field
    var $other = $(page)
        .find('.other_input')
        .keyup(function() {
            question.answer[question.choices.length] = { 
                response: self._validate("text", this.value, question.logic),
                failed_validation: Boolean(null === self._validate('text', this.value, question.logic)),
                metadata: {
                    'type_exception': 'other',
                },
            }
        });


    // Hide input by default
    $other.hide();

    // Deal with select (multiple or not)
    $(page)
        .find('select')
        .change(function() {
            // any change => answer is reset
            question.answer = [];
            $other.hide();

            // jquery is dumb and inconsistent with val type
            var svals = $('select').val(); 
            svals = typeof svals === 'string' ? [svals] : svals;

            // find all select options
            svals.forEach(function(opt) { 

                var ind = choices.indexOf(opt);
                
                // Please choose something option wipes answers
                if (opt === 'null') { 
                    return;
                }

                // Default, fill in values (other will be overwritten below if selected)
                question.answer[ind] = {
                    response: opt,
                    metadata: {}
                }

                if (opt === 'other') {
                    question.answer[ind] = {
                        response: $other.val(), // Preserves prev response
                        metadata: {
                            'type_exception': 'other',
                        },
                    }

                    $other.show();
                } 
             });

        });

    // Selection is handled in _template however toggling of view is done here
    var response = question.answer[question.choices.length];
    if (response 
            && response.metadata.type_exception === 'other') {
        $other.show();
    }
};

/* 
 * Photo Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 *
 * Note: Disables input field change handler.
 * XXX IN PROGRESSS
 */
Widgets.photo = function(question, page, footer) {
    this._input(question, page, footer, "photo");
    var self = this;
    var playing = false;
    var video = $('.question__video')[0];

    // Camera selection
    var camera = null;
    if (window.MediaStreamTrack){
        // Save the last camera id. It's likely the outward facing one.
        MediaStreamTrack.getSources(function(sources) {
            sources.forEach(function(source) {
                if (source.kind == 'video') {
                    camera = source.id;
                }
            });
        });
    }

    // Browser implementations
    navigator.getUserMedia = navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia;

    // Start video immediately 
    navigator.getUserMedia({
        video: {optional: [{sourceId: camera}]}
    }, function(stream) {
        video.src = window.URL.createObjectURL(stream);
        video.play();
        playing = true;
    }, function(err) {
        console.log("Video failed:", err);
    });

    // Set up canvas
    var canvas = $('.question__canvas')[0];
    canvas.width = 320; //redundant
    canvas.height = 240;
    var context = canvas.getContext('2d');


    function updatePhoto(video, canvas, context) {
        // Find current length of inputs and update the last one;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        var photo = canvas.toDataURL("image/png", 0.5);

        // Tests
        window.photo = photo;
        //var img = $('<img>')
        //img.attr('src', photo);
        //img.appendTo(page);

        // update array val
        var questions_len = $(page).find('.text_input').length;
        question.answer[questions_len - 1] = {
            response: photo,
            metadata: {},
        }            

        // update latest lon/lat values
        var questions_len = $(page).find('.text_input').length;
        $(page).find('.text_input')
            .last().val(photo);
    }


    window.video = video;
    window.context = context;
    window.canvas = canvas;

    // Add photo
    $(page)
        .find('.question__photo__btn')
        .click(function() {
            if (playing) {
                video.pause();
                navigator.vibrate(50);
                updatePhoto(video, canvas, context);
                playing = false;
                $('.question__photo__btn')
                    .find('.btn_text')
                    .text('click to redo photo');
            } else {
                video.play();
                playing = true;
                $('.question__photo__btn')
                    .find('.btn_text')
                    .text('take a photo');
            }
        });


    // Disable default event
    $(page)
        .find('.text_input')
        .off('keyup');
};


/* 
 * Location Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 *
 * Note: Disables input field change handler.
 */
Widgets.location = function(question, page, footer) {
    // generic setup
    this._input(question, page, footer, "location");

    var self = this;
    var response = $(page).find('.text_input').last().val();
    response = self._validate('location', response, question.logic);

    function updateLocation(coords) {
        // Find current length of inputs and update the last one;
        var questions_len = $(page).find('.text_input').length;

        // update array val
        question.answer[questions_len - 1] = {
            response: {'lon': coords.lon, 'lat': coords.lat},
            metadata: {},
        }
            
        // update latest lon/lat values
        var questions_len = $(page).find('.text_input').length;
        $(page).find('.text_input')
            .last().val(coords.lat + " " + coords.lon);
    }

    // Find me
    $(page)
        .find('.question__find__btn')
        .click(function() {
            //App.message('Searching ...', 'message-primary');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var loc = {
                        'lat': position.coords.latitude,
                        'lon': position.coords.longitude, 
                    }

                    App.location = loc;
                    updateLocation(loc); //XXX: DONT MOVE ON

                }, function error() {
                    //If cannot Get location" for some reason,
                    App.message('Could not get your location, please make sure your GPS device is active.', 'Survey GPS Error', 'message-warning');
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });

    // Disable default event
    $(page)
        .find('.text_input')
        .off('keyup');
};

/* 
 * Facility Widget
 *
 * Toggles between two widget states: 
 *      add facilities state 
 *      select facility state
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 *
 */
Widgets.facility = function(question, page, footer) {
    // Hide add button by default
    $('.facility__btn').hide();
    console.log(question.answer[0])

    // Default operation on caputre Location 
    var captureCallback = reloadFacilities;
    if (question.answer[0] && question.answer[0].metadata.is_new) {
        console.log('new facility chosen');
        captureCallback = updateLocation;
        //$('.question__map').hide();
        $('.facility__btn').show();
        $('.question__radios').hide();
        $('.question__add__facility').show();
        $('.facility__btn').text("cancel");
    }

    // Revisit API Call calls facilitiesCallback
    drawFacilities(App.facilities);

    /* Helper functions for updates  */
    function reloadFacilities(loc) {
        if (navigator.onLine) {
            // Refresh if possible
            getNearbyFacilities(loc.lat, loc.lon, 
                    FAC_RAD, // Radius in km 
                    NUM_FAC, // limit
                    drawFacilities // what to do with facilities
                );

        } else {
            drawFacilities(App.facilities); // Otherwise draw our synced facilities
        }
    }

    /*
     * Create radio buttons for the nearest facilities in facilities_dict.
     *
     * @facilities_dict: A dict of facilities with the facility uuids as keys
     */
    function drawFacilities(facilities_dict) {

        var loc = App.location;
        if (Object.keys(loc).length == 0) {
            console.log("No location found\n");
            $('.facility__btn').hide();
            return;
        }

        var facilities = [];
        Object.keys(facilities_dict).forEach(function(uuid) {
           facilities.push(facilities_dict[uuid]);
        });

        console.log(facilities);

        var ans = question.answer[0];
        var selected = ans && ans.response.facility_id || null;

        // http://www.movable-type.co.uk/scripts/latlong.html
        function latLonLength(coordinates, loc) {
            var R = 6371000; // metres
            var e = loc.lat * Math.PI/180;
            var f = coordinates[1] * Math.PI/180;
            var g = (coordinates[1] - loc.lat) * Math.PI/180;
            var h = (coordinates[0] - loc.lon) * Math.PI/180;

            var a = Math.sin(g/2) * Math.sin(g/2) +
                    Math.cos(e) * Math.cos(f) *
                    Math.sin(h/2) * Math.sin(h/2);

            var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

            return R * c;
        }

        facilities.sort(function(facilityA, facilityB) {
            var lengthA = latLonLength(facilityA.coordinates, loc);
            var lengthB = latLonLength(facilityB.coordinates, loc);
            return (lengthA - lengthB); 
        });

        $('.facility__btn').show();
        $(".question__radios").empty();
        for(var i=0; i < Math.min(10, facilities.length); i++) {
            var uuid = facilities[i].uuid;
            var name = facilities[i]["name"];
            var sector = facilities[i]["properties"]["sector"];
            var distance = latLonLength(facilities[i].coordinates, loc).toFixed(2) + "m";
            var $div = addNewButton(uuid, name, sector, distance, ".question__radios");
            if (selected === uuid) {
                    $div.find('input[type=radio]').prop('checked', true);
                    //$div.addClass('question__radio__selected');
            }
        }
    } 


    /*
     * Create and append a radio button
     * @value: value to be stored in value field of button
     * @name: label to be displayed next to button
     * @sector: sector to be displayed under button
     * @distance: distance to be displayed under button
     * @region: where to append new button.
     */
    function addNewButton(value, name, sector, distance, region) {
        var div_html = "<div class='question__radio'>"
            + "<input type='radio' id='"+ value + "' name='facility' value='"+ value +"'/>"
            + "<label for='" + value + "'>"
            + "<span class='question__radio__span__btn'><span></span></span>"
            + name + "</label>"
            + "<br/><span class='question__radio__span__meta'>"+ sector +"</span>"
            + "<span class='question__radio__span__meta'><em>"+ distance +"</em></span>"
            + "</div>";

        $div = $(div_html);
        $(region).append($div);
        return $div;
    }

    /* Handle events */

    // Radios 
    $(page)
        .find('.question__radios')
        .delegate('.question__radio', 'click', function(e) {
            e.stopImmediatePropagation();
            e.stopPropagation();
            e.preventDefault();
            var rbutton = $(this).find('input[type=radio]').first();
            var uuid = rbutton.val();
            var ans = question.answer[0];
            var selected = ans && ans.response.facility_id || null;

            if (selected === uuid) {
                rbutton.prop('checked', false);
                //$(this).removeClass('question__radio__selected');
                question.answer = [];
                return;
            }

            var coords = App.facilities[uuid].coordinates; // Should always exist
            var name = App.facilities[uuid].name;
            var sector = App.facilities[uuid]['properties'].sector;
            question.answer = [{ 
                response: {
                    'facility_id': uuid, 
                    'lat': coords[1], 
                    'lon': coords[0], 
                    'facility_name': name, 
                    'facility_sector': sector 
                },
                metadata : {}
            }];

            
            rbutton.prop('checked', true);

        });

    // Find me
    $(page)
        .find('.question__find__btn')
        .click(function() {
            //App.message('Searching ...', 'message-primary');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var loc = {
                        'lat': position.coords.latitude,
                        'lon': position.coords.longitude, 
                    }

                    // Remember response
                    App.location = loc;

                    // Revisit api call
                    captureCallback(loc); 
        
                    // Make sure button is visible now
                    $('.facility__btn').show();

                }, function error() {
                    App.message('Could not get your location, please make sure your GPS device is active.', 'Survey GPS Error',
                            'message-warning');
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });


    // Add facility
    $(page)
        .find('.facility__btn')
        .click(function() {
            if (question.answer[0] && question.answer[0].metadata.is_new) {
                $('.facility__btn').text("add new facility");
                question.answer = [];
                $('.question__add__facility').hide();
                //$('.question__map').show();
                $('.question__radios').show();
                captureCallback = reloadFacilities;
            } else {
                $('.facility__btn').text("cancel");
                if (question.answer[0] && question.answer[0].response.facility_id) {
                    var rbutton = $('.question__radios').find("input[value='"+ question.answer[0].response.facility_id +"']");
                    rbutton.prop('checked', false);
                    //$(this).removeClass('question__radio__selected');
                }

                //$('.question__map').hide();
                $('.question__radios').hide();
                $('.question__add__facility').show();

                var uuid = $('.facility_uuid_input').val() || objectID();
                var lat = $('.facility_location_input').val().split(" ")[0] || App.location.lat;
                var lon = $('.facility_location_input').val().split(" ")[1] || App.location.lon;
                var name = $('.facility_name_input').val();
                var sector = $('.facility_sector_input').val();

                question.answer = [{ 
                    response: {
                        'facility_id': uuid, 
                        'lat': lat, 
                        'lon': lon, 
                        'facility_name': name, 
                        'facility_sector': sector, 
                    },
                    metadata : {
                        'is_new': true
                    },
                    failed_validation: Boolean(!name || !sector)  
                }];

                $('.facility_uuid_input').val(uuid);
                $('.facility_location_input').val(lat + " " + lon);
                $('.facility_name_input').val(name);
                $('.facility_sector_input').val(sector);

                captureCallback = updateLocation;
            }

            console.log(question.answer[0]);

        });

    // Name input
    $(page)
        .find('.facility_name_input')
        .keyup(function() {
            var name = this.value;
            var sector = question.answer[0].facility_sector;
            question.answer[0].facility_name = name;
            question.answer[0].failed_validation = Boolean(!name || !sector);
        });

    // Sector input 
    $(page)
        .find('.facility_sector_input')
        .change(function() {
            var sector = this.value;
            var name = question.answer[0].facility_name;
            question.answer[0].facility_sector = sector;
            question.answer[0].failed_validation = Boolean(!name || !sector);
        });

    // Location callback 
    function updateLocation(loc) {
       $('.facility_location_input').val(loc.lat + " " + loc.lon);
       question.answer[0].response.lat = loc.lat;
       question.answer[0].response.lon = loc.lon;
    }

};

exports.Widgets = Widgets; 

},{"./facilities.js":1}],4:[function(require,module,exports){
var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

var getNearbyFacilities = require('./facilities.js').getNearbyFacilities;
var postNewFacility = require('./facilities.js').postNewFacility;
var Widgets = require('./widgets.js').Widgets;
var Survey = require('./survey.js').Survey;

// In memory variables used across the webapp
var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    location: {},
    submitter_name: '',
    submitter_email: '',
    survey: null,
};

/*
 * Initilize the webapp by creating a new survey, and reading any values saved 
 * in storage. Function is called on page load.
 *
 * @survey: JSON representation of the survey
 */
App.init = function(survey) {
    var self = this;

    var answers = JSON.parse(localStorage[survey.id] || '{}');
    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name || "";
    self.submitter_email = localStorage.email || "";
    
    console.log(survey.nodes);
    self.survey = new Survey(survey.id, 
            survey.version, 
            survey.nodes, 
            answers,
            survey.metadata, 
            survey.title[survey.default_language], 
            survey.created_on,
            survey.last_update_time,
            survey.default_language
            );

    // Set up an empty dictonary if no unsynced surveys are found
    if (!localStorage.unsynced) {
        localStorage.unsynced = JSON.stringify({});
    }

    // Load up any unsynced submissions
    App.unsynced = JSON.parse(localStorage.unsynced)[self.survey.id] || []; 
    // Set up survey location
    App.location = answers['location'] 
        || survey.metadata.location 
        //|| {'lat': 40.8138912, 'lon': -73.9624327};
        || {};


    // Load up any unsynced facilities
    App.unsynced_facilities = 
        JSON.parse(localStorage.unsynced_facilities || "{}");

    // Load any facilities
    App.facilities = JSON.parse(localStorage.facilities || "{}");
    if (JSON.stringify(App.facilities) === "{}" && navigator.onLine) {
        // See if you can get some new facilities
        getNearbyFacilities(App.location.lat, App.location.lon, 
            FAC_RAD, // Radius in km 
            NUM_FAC, // limit
            null// what to do with facilities 
        );
    }

    // Listen to appcache updates, reload JS.
    window.applicationCache.addEventListener('updateready', function() {
        console.log('app updated, reloading...');
        window.location.reload();
    });

    // Clicking burger
    $('header')
        .on('click', '.menu', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();
        });

    // Clear all survey data
    $('header')
        .on('click', '.menu_clear', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            localStorage.clear();
            App.splash();
            window.location.reload();
            App.message('All survey data erased.', 'Surveys Nuked', 'message-warning');
        });

    // Clear active survey data
    $('header')
        .on('click', '.menu_restart', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            App.clearState();
            App.splash();
            window.location.reload();
            App.message('Active survey has been cleared.', 'Survey Reset', 'message-warning');
        });

    // Save active survey state
    $('header')
        .on('click', '.menu_save', function(e) {
            $('header').toggleClass('title-extended');
            $('.title_menu').toggle();

            App.saveState();
            App.message('Active survey has been saved.', 'Survey Saved', 'message-success');
        });
        
    // Begin survey at Application splash page
    App.splash();
};

/*
 * Submit all unsynced surveys to Dokomoforms. Should only be called on when 
 * device has a web connection. Calls App.submit
 *
 * Removes successfully submitted survey from unsynced array and localStorage. 
 * Launches modal on completion.
 */
App.sync = function() {
    var self = this;
    //$('.submit_modal')[0].click(); // Pop Up Submitting Modal
    self.countdown = App.unsynced.length; //JS is single threaded no race condition counter
    self.count = App.unsynced.length; //JS is single threaded no race condition counter
    var endSync = function() {
        //$('.submit_modal')[0].click(); // Remove submitting modal;
        App.splash();
        if (!App.unsynced.length) {
            App.message('All ' + self.count + ' surveys synced succesfully.', 
                    'Survey Synced', 'message-success');
        } else {
            App.message(App.unsynced.length + ' survey(s) failed to sync succesfully. Please try again later.', 
                    'Survey Sync Failed', 'message-error');
        }
    };
    _.each(App.unsynced, function(survey) {
        App.submit(survey, 
            function(survey) { 
                console.log('done');
                // Has to be there
                var idx = App.unsynced.indexOf(survey);
                App.unsynced.splice(idx, 1);
                var unsynced = JSON.parse(localStorage.unsynced); 
                unsynced[self.survey.id] = App.unsynced;
                localStorage['unsynced'] = JSON.stringify(unsynced);
                --self.countdown; 
                
                if (self.countdown === 0) {  
                    endSync();
                }
            },

            function(err, survey) { 
                console.log('fail');
                window.err = err;
                --self.countdown; 

                if (self.countdown === 0) {
                    endSync();
                }
            } 
        );
    });

    // Attempt to submit unsynced facilities to Revisit
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });
};

/*
 * Trigger modal event, powered by ratchet. 
 *
 * @text: modal message
 * @title: modal title
 * @style: modal type (possible classes in css)
 */
App.message = function(text, title, style) {
    $('.message_btn')[0].click();
    
    $('.modal_header').empty()
        // Remove any posible class attached to modal div
        .removeClass('message-primary')
        .removeClass('message-error')
        .removeClass('message-warning')
        .removeClass('message-success')
        // Attach requested class
        .addClass(style)
        .text(title);

    // Message text region
    $('.message')
        .text(text);
};

/* 
 * Webapp splash page, text loaded from template.
 * This is where user syncs and starts surveys.
 */ 
App.splash = function() {
    $('header').removeClass('title-extended');
    $('.title_menu').hide();
    var self = this;
    var survey = self.survey;
    $('.overlay').hide(); // Always remove overlay after moving.

    // Update page nav and footer
    var barnav  = $('.bar-nav');
    var barnavHTML = $('#template_nav__splash').html();
    var barnavTemplate = _.template(barnavHTML);
    var compiledHTML = barnavTemplate({
        'org': survey.org,
    });
    
    barnav.empty()
        .html(compiledHTML);

    var barfoot = $('.bar-footer');
    barfoot.removeClass('bar-footer-extended');
    barfoot.removeClass('bar-footer-super-extended');
    barfoot.css("height", "");

    var barfootHTML = $('#template_footer__splash').html();
    var barfootTemplate = _.template(barfootHTML);
    compiledHTML = barfootTemplate({
    });

    barfoot.empty()
        .html(compiledHTML)
        .find('.start_btn')
        .one('click', function() {
            // Render first question
            App.survey.render(App.survey.first_question);
        });


    // Set up content
    var content = $('.content');
    content.removeClass('content-shrunk');
    content.removeClass('content-super-shrunk');

    var splashHTML = $('#template_splash').html();
    var splashTemplate = _.template(splashHTML);
    compiledHTML = splashTemplate({
        'survey': survey,
        'online': navigator.onLine,
        'name': App.submitter_name,
        'unsynced': App.unsynced,
        'unsynced_facilities': App.unsynced_facilities
    });

    content.empty()
        .data('index', 0)
        .html(compiledHTML)
        .find('.sync_btn')
        .one('click', function() {
            if (navigator.onLine) {
                App.sync();
            } else {
                App.message('Please connect to the internet first.', 'Connection Error', 'message-warning');
            }
        });
};

/*
 * Submits a single survey to Dokomoforms.
 *
 * @survey: Object representation of a completed survey
 * @done: Successful submission callback
 * @fail: Failed submission callback
 */
App.submit = function(survey, done, fail) {
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    
    // Update submit time
    survey.submission_time = new Date().toISOString();

    $.ajax({
        url: '/api/v0/surveys/'+survey.survey_id+'/submit',
        type: 'POST',
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(survey),
        headers: {
            "X-XSRFToken": getCookie("_xsrf")
        },
        dataType: 'json',
        success: function() {
            done(survey);
        },
        error: function(err, anything) {
            console.log(anything);
            fail(err, survey);
        }
    });

    console.log('synced submission:', survey);
    console.log('survey', '/api/v0/surveys/'+survey.survey_id+'/submit');
}

/*
 * Save the current state of the survey (i.e question answers) to localStorage.
 */
App.saveState = function() {

    // Save answers in storage
    var answers = this.survey.getState();
    localStorage[this.survey.id] = JSON.stringify(answers);
};

/*
 * Clear the current state of the survey (i.e question answers) and remove the 
 * state in localStorage.
 */
App.clearState = function() {

    // Reset location
    App.location = {};

    // Clear answers locally
    this.survey.clearState();

    // Clear answers in localStorage
    localStorage[this.survey.id] = JSON.stringify({});
}

// For requiring
exports = exports || {};
exports.App = App;

// For window
window = window || {};
window.App = App;

},{"./facilities.js":1,"./survey.js":2,"./widgets.js":3}]},{},[4]);
