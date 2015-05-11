var NEXT = 1;
var PREV = -1;
var ON = true;
var OFF = false;
var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    location: {},
    submitter_name: ''
};

App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, 
            survey.survey_version, 
            survey.questions, 
            survey.survey_metadata, 
            survey.survey_title, 
            survey.created_on,
            survey.last_updated);

    var start_loc = survey.survey_metadata.location 
        || {'lat': 40.8138912, 'lon': -73.9624327}; // defaults to nyc

    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name || "";
    self.submitter_email = localStorage.email || "";
    
    // Init if unsynced is undefined
    if (!localStorage.unsynced) {
        localStorage.unsynced = JSON.stringify({});
    }
    // Load up any unsynced submissions
    App.unsynced = JSON.parse(localStorage.unsynced)[self.survey.id] || []; 

    // Load up any unsynced facilities
    App.unsynced_facilities = 
        JSON.parse(localStorage.unsynced_facilities || "{}");

    // Load any facilities
    App.facilities = JSON.parse(localStorage.facilities || "{}");
    if (JSON.stringify(App.facilities) === "{}" && navigator.onLine) {
        // See if you can get some new facilities
        getNearbyFacilities(start_loc.lat, start_loc.lon, 
            FAC_RAD, // Radius in km 
            NUM_FAC, // limit
            null// what to do with facilities 
        );
    }

    $('.sel')
        .click(function(e) {
            e.preventDefault();
            self.sync();
        });
        
    // AppCache updates
    window.applicationCache.addEventListener('updateready', function() {
        alert('app updated, reloading...');
        window.location.reload();
    });

    App.splash();
};

App.sync = function() {
    var self = this;
    self.countdown = App.unsynced.length; //JS is single threaded no race condition counter
    _.each(App.unsynced, function(survey, idx) {
        App.submit(survey, 
            function(survey) { 
                console.log('done');
                App.unsynced.splice(idx, 1);
                var unsynced = JSON.parse(localStorage.unsynced); 
                unsynced[self.survey.id] = App.unsynced;
                localStorage['unsynced'] = JSON.stringify(unsynced);
                --self.countdown; 
                
                if (self.countdown === 0) 
                    App.splash();
            },

            function(survey) { 
                console.log('fail');
                --self.countdown; 

                if (self.countdown === 0) 
                    App.splash();
            } 
        );
    });

    // Facilities junk
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });
};

App.message = function(text, style) {
    // Shows a message to user
    // E.g. "Your survey has been submitted"
    $('.message_btn')[0].click();
    $('.modal_content').empty();
    

    var message =  $('<div></div>')
        .addClass('message_main')
        .addClass('message')
        .addClass('content-padded')
        .addClass(style)
        .text(text)

     var okay =  $('<div></div>')
        .addClass('content-padded');

     $('<a href="#message"></a>')
        .addClass('btn')
        .addClass('btn-block')
        .addClass('btn-netural')
        .addClass('message_sub')
        .text('OK')
        .appendTo(okay);

    message.appendTo('.modal_content');
    okay.appendTo('.modal_content');

};

App.splash = function() {
    var self = this;
    var survey = self.survey;
    $('.overlay').hide(); // Always remove overlay after moving

    // Update page nav bar
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
                // Reload page to update template values
                App.splash();
            } else {
                App.message('Please connect to the internet first.', 'message-box-warning');
            }
        });
};

App.submit = function(survey, done, fail) {
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    
    // Update submit time
    survey.submission_time = new Date().toISOString();

    $.ajax({
        url: '/api/surveys/'+survey.survey_id+'/submit',
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
        error: function() {
            fail(survey);
        }
    });

    console.log('synced submission:', survey);
    console.log('survey', '/api/surveys/'+survey.survey_id+'/submit');
}

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
        //XXX Shouldn't show splash page right 
        //App.splash();
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
            + self.current_question.type_constraint_name, 'message-box-error');
            return;
        }

        // Are you required?
        if (this.current_question.logic.required && (first_response === null)) {
            App.message('Survey requires this question to be completed.', 'message-box-error');
            return;
        }

        // Is the only response and empty is other response?
        if (first_is_type_exception && !first_response) {
            App.message('Please provide a reason before moving on.', 'message-box-error');
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
            App.message('Saving failed, No questions answer in Survey!', 'message-box-warning');
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

    App.message('Saved Submission!', 'message-box-primary');
    App.splash();


};


var Widgets = {
    interval: null,
};

// This widget's events. Called after page template rendering.
// Responsible for setting the question object's answer
//
// question: question data
// page: the widget container DOM element
// type: type of widget, handles all accept
//
//      multiple choice
//      facility
//      note
//
// All widgets store results in the questions.answer array
Widgets._input = function(question, page, footer, type) {
    var self = this;
    
    // Render add/minus input buttons 
    self._renderRepeat(page, footer, type, question);

    //Render don't know
    self._renderOther(page, footer, type, question);

    // Clean up answer array, short circuits on is_type_exception responses
    self._orderAnswerArray(page, footer, question, type);

    // Set up input event listner
    $(page)
        .find('.text_input')
        .keyup(function() { //XXX: Change isn't sensitive enough on safari?
            var ans_ind = $(page).find('input').index(this); 
            question.answer[ans_ind] = { 
                response: self._validate(type, this.value, question.logic),
                is_type_exception: false,
                failed_validation: !Boolean(self._validate(type, this.value, question.logic)),
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

// Handle creating multiple inputs for widgets that support it 
Widgets._addNewInput = function(page, input, question) {
    if (question.allow_multiple) { //XXX: Technically this btn clickable => allow_multiple 
        input.parent()
            .clone(true)
            .insertAfter(input.parent())
            .find('input')
            .val(null)
            .focus();
    }
};

Widgets._removeInput = function(page, footer, type, inputs, question, index) {
    var self = this;
    if (question.allow_multiple && (inputs.length > 1)) { //XXX: Technically this btn clickable => allow_multiple 
        delete question.answer[index];
        $(inputs[index]).parent().remove();
        self._orderAnswerArray(page, footer, question, type);
    } else {
        // atleast wipe the value
        delete question.answer[index];
        $(inputs[index]).val(null);

    }

    inputs
        .last()
        .focus()
};

Widgets._orderAnswerArray = function(page, footer, question, type) {
    question.answer = []; //XXX: Must be reinit'd to prevent sparse array problems
    var self = this;

    $(page).find('.text_input').each(function(i, child) { 
        if (child.value !== "") {
            question.answer[i] = {
                response: self._validate(type, child.value, question.logic),
                is_type_exception: false,
                failed_validation: !Boolean(self._validate(type, this.value, question.logic)),
                metadata: {}
            }
        }
    });

    $(footer).find('.dont_know_input').each(function(i, child) { 
        if (!child.disabled) {
            // if don't know input field has a response, break 
            question.answer = [{
                response: self._validate('text', child.value, question.logic),
                is_type_exception: true,
                failed_validation: !Boolean(self._validate('text', this.value, question.logic)),
                metadata: {
                    'type_exception': 'dont_know',
                },

            }];

            // there should only be one
            return false;
        }
    });
}

// Render 'don't know' section if question has with_other logic
// Display response and alter widget state if first response is other
Widgets._renderOther = function(page, footer, type, question) {
    var self = this;
    // Render don't know feature 
    if (question.logic.allow_dont_know) {
        $('.question__btn__other').show();
        footer.addClass('bar-footer-extended');
        page.addClass('content-shrunk');


        var repeatHTML = $('#template_dont_know').html();
        var widgetTemplate = _.template(repeatHTML);
        var compiledHTML = widgetTemplate({question: question});
        $(footer).append(compiledHTML);

        var other_response = question.answer && question.answer[0] && question.answer[0].is_type_exception && question.answer[0].metadata.type_exception === "dont_know";
        if (other_response) {
            $('.question__btn__other').find('input').prop('checked', true);
            this._toggleOther(page, footer, type, question, ON);
        }

        // Click the other button when you don't know answer
        $(footer)
            .find('.question__btn__other :checkbox')
            .change(function() { 
                var selected = $(this).is(':checked'); 
                self._toggleOther(page, footer, type, question, selected);
            });


        // Set up other input event listener
        $(footer)
            .find('.dont_know_input')
            .keyup(function() { //XXX: Change isn't sensitive enough on safari?
                question.answer = [{ 
                    response: self._validate('text', this.value, question.logic),
                    is_type_exception: true,
                    failed_validation: !Boolean(self._validate('text', this.value, question.logic)),
                    metadata: {
                        'type_exception': 'dont_know',
                    },
                }];
            });

        }
}

// Toggle the 'don't know' section based on passed in state value on given page
// Alters question.answer array
Widgets._toggleOther = function(page, footer, type, question, state) {
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
                is_type_exception: true,
                failed_validation: !Boolean(self._validate('text', this.value, question.logic)),
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
                    failed_validation: !Boolean(self._validate(type, this.value, question.logic)),
                    is_type_exception: false,
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

// Render +/- buttons on given page
Widgets._renderRepeat = function(page, footer, type, question) {
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
                self._addNewInput(page, input, question);

            });

        // Click the - to remove that element
        $(page)
            .find('.question__minus')
            .click(function() { 
                var delete_icons = $(page).find('.question__minus');
                var inputs = $(page).find('.text_input');
                var index = delete_icons.index(this);
                self._removeInput(page, footer, type, inputs, question, index);
            });
    }
}

// Basic input validation
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

Widgets.text = function(question, page, footer) {
    this._input(question, page, footer, "text");
};

Widgets.integer = function(question, page, footer) {
    this._input(question, page, footer, "integer");
};

Widgets.decimal = function(question, page, footer) {
    this._input(question, page, footer, "decimal");
};

Widgets.date = function(question, page, footer) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, footer, "date"); //XXX: Fix validation
};

Widgets.time = function(question, page, footer) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, footer, "time"); //XXX: Fix validation
};

Widgets.note = function() {
};

// Multiple choice and multiple choice with other are handled here by same func
// XXX: possibly two widgets (multi select and multi choice)
Widgets.multiple_choice = function(question, page, footer) {
    var self = this;

    // array of choice uuids
    var choices = [];
    question.choices.forEach(function(choice, ind) {
        choices[ind] = choice.question_choice_id;
    }); 
    choices[question.choices.length] = "other"; 


    //Render don't know
    self._renderOther(page, footer, 'multiple_choice', question);

    // handle change for text field
    var $other = $(page)
        .find('.other_input')
        .keyup(function() {
            question.answer[question.choices.length] = { 
                response: self._validate("text", this.value, question.logic),
                failed_validation: !Boolean(self._validate('text', this.value, question.logic)),
                is_type_exception: true,
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
                    is_type_exception: false,
                    metadata: {}
                }

                if (opt === 'other') {
                    question.answer[ind] = {
                        response: $other.val(), // Preserves prev response
                        is_type_exception: true,
                        metadata: {
                            'type_exception': 'other',
                        },
                    }

                    $other.show();
                } 
             });

            // Toggle off other if deselected on change event 
            //if (svals.indexOf('other') < 0) { 
            //    $other.hide();
            //}
            
        });

    // Selection is handled in _template however toggling of view is done here
    var response = question.answer[question.choices.length];
    if (response 
            && response.is_type_exception 
            && response.metadata.type_exception === 'other') {
        $other.show();
    }
};

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
            is_type_exception: false,
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
            //App.message('Searching ...', 'message-box-primary');
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
                    App.message('Could not get your location, please make sure your GPS device is active.', 'message-box-warning');
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

// Similar to location however you cannot just add location, 
Widgets.facility = function(question, page, footer) {
    // Hide add button by default
    $('.facility__btn').hide();

    // Default operation on caputre Location 
    var captureCallback = reloadFacilities;
    if (question.answer[0] && question.answer[0].metadata.is_new) {
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

    // handles calling drawPoint gets called once per getNearby call 
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
        var selected = ans && ans.response.id || null;

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
            if (question.answer[0] && question.answer[0].response.id === uuid) {
                    $div.find('input[type=radio]').prop('checked', true);
                    //$div.addClass('question__radio__selected');
            }
        }
    } 


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

            var rbutton = rbutton;
            if (question.answer[0] && question.answer[0].response.id === uuid) {
                rbutton.prop('checked', false);
                //$(this).removeClass('question__radio__selected');
                question.answer = [];
                return;
            }

            var coords = App.facilities[uuid].coordinates; // Should always exist
            var name = App.facilities[uuid].name;
            var sector = App.facilities[uuid]['properties'].sector;
            question.answer = [{ 
                response: {'id': uuid, 'lat': coords[1], 'lon': coords[0] },
                metadata: {'name': name, 'sector': sector }
            }];

            
            //$(this).addClass('question__radio__selected');
            rbutton.prop('checked', true);

        });

    // Find me
    $(page)
        .find('.question__find__btn')
        .click(function() {
            //App.message('Searching ...', 'message-box-primary');
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
                    App.message('Could not get your location, please make sure your GPS device is active.',
                            'message-box-warning');
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
                if (question.answer[0] && question.answer[0].response.id) {
                    var rbutton = $('.question__radios').find("input[value='"+ question.answer[0].response.id +"']");
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
                    response: {'id': uuid, 'lat': lat, 'lon': lon },
                    metadata: {'name': name, 'sector': sector, 'is_new': true },
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
            question.answer[0].metadata.name = this.value;
            var name = this.value;
            var sector = question.answer[0].metadata.sector;
            question.answer[0].failed_validation = Boolean(!name || !sector);
        });

    // Sector input 
    $(page)
        .find('.facility_sector_input')
        .change(function() {
            question.answer[0].metadata.sector = this.value;
            var sector = this.value;
            var name = question.answer[0].metadata.name;
            question.answer[0].failed_validation = Boolean(!name || !sector);
        });

    // Location callback 
    function updateLocation(loc) {
       $('.facility_location_input').val(loc.lat + " " + loc.lon);
       question.answer[0].response.lat = loc.lat;
       question.answer[0].response.lon = loc.lon;
    }

};


/* -------------------------- Revisit Stuff Below ----------------------------*/
function getNearbyFacilities(lat, lng, rad, lim, cb) {
    var url = "http://staging.revisit.global/api/v0/facilities.json"; 

    // Revisit ajax req
    //console/g.log("MADE EXTERNAL REVISIT QUERY");
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
            //App.message('Facility Added!', 'message-box-primary');
            // If posted, we don't an unsynced reference to it anymore
            delete App.unsynced_facilities[facility.uuid];
        },
        
        headers: {
            "Authorization": "Basic " + btoa("dokomoforms" + ":" + "password")
                //DONT DO THIS XXX XXX
        },

        error: function() {
            //App.message('Facility submission failed, will try again later.', 'message-box-warning');
        },
        
        complete: function() {
            localStorage.setItem("facilities", 
                    JSON.stringify(App.facilities));

            localStorage.setItem("unsynced_facilities", 
                    JSON.stringify(App.unsynced_facilities));

        }
    });
}

// Def not legit but hey
function objectID() {
    return 'xxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[x]/g, function() {
        var r = Math.random()*16|0;
        return r.toString(16);
    });
}

var exports = exports || {} //XXX: Just to silence console; 
exports.App = App;
exports.Survey = Survey;
exports.Widgets = Widgets; 
exports.getNearbyFacilities = getNearbyFacilities;
exports.postNewFacility = postNewFacility;
