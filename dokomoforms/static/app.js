var NEXT = 1;
var PREV = -1;
var ON = true;
var OFF = false;
var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

var appCache = window.applicationCache;
switch (appCache.status) {
    case appCache.UNCACHED: // UNCACHED == 0
        console.log('UNCACHED');
        break;
    case appCache.IDLE: // IDLE == 1
        console.log('IDLE');
        break;
    case appCache.CHECKING: // CHECKING == 2
        console.log('CHECKING');
        break;
    case appCache.DOWNLOADING: // DOWNLOADING == 3
        console.log('DOWNLOADING');
        break;
    case appCache.UPDATEREADY:  // UPDATEREADY == 4
        console.log('UPDATEREADY');
        break;
    case appCache.OBSOLETE: // OBSOLETE == 5
        console.log('OBSOLETE');
        break;
    default:
        console.log('UKNOWN CACHE STATUS');
        break;
};

var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    start_loc: {'lat': 40.8138912, 'lon': -73.9624327}, // defaults to nyc, updated constantly
    tile_url: 'http://{s}.tiles.mapbox.com/v3/examples.map-20v6611k/{z}/{x}/{y}.png',
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

    self.start_loc = survey.survey_metadata.location || self.start_loc;
    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name || "";
    self.submitter_email = localStorage.email || "";
    
    // Load any facilities
    if (App.facilities.length === 0) {
        // See if you can get some new facilities
        getNearbyFacilities(App.start_loc.lat, App.start_loc.lon, 
            FAC_RAD, // Radius in km 
            NUM_FAC, // limit
            null// what to do with facilities 
        );
    }

    // Init if unsynced is undefined
    if (!localStorage.unsynced) {
        localStorage.unsynced = JSON.stringify({});
    }
    
    // Load up any unsynced submissions
    App.unsynced = JSON.parse(localStorage.unsynced)[self.survey.id] || []; 

    // Load up any unsynced facilities
    App.unsynced_facilities = 
        JSON.parse(localStorage.unsynced_facilities || "{}");

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
    self.countdown = App.unsynced.length; //JS is single threaded, no race condition on counter
    self.failed = [];
    var restore = function() {
        // Were done!
        App.unsynced = self.failed;
        self.failed = [];
        var unsynced = JSON.parse(localStorage.unsynced); 
        unsynced[self.survey.id] = App.unsynced;
        localStorage['unsynced'] = JSON.stringify(unsynced);

        // Reload page to update template values
        App.splash();
    };
    _.each(App.unsynced, function(survey, idx) {
        App.submit(survey, 
            function(survey) { 
                //console.log('done');
                --self.countdown; 
                
                if (self.countdown === 0) 
                    restore();
            },

            function(survey) { 
                //console.log('fail');
                --self.countdown; 
                App.failed.push(survey);

                if (self.countdown === 0) 
                    restore();
            } 
        );
    });

    // Facilities junk
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });

    App.unsynced = [];
    var unsynced = JSON.parse(localStorage.unsynced); 
    unsynced[self.survey.id] = App.unsynced;
    localStorage['unsynced'] = JSON.stringify(unsynced);
    console.log('localStorage', localStorage.unsynced);
};

App.message = function(text, style) {
    // Shows a message to user
    // E.g. "Your survey has been submitted"
    $('<div></div>')
        .addClass('message')
        .addClass(style)
        .text(text)
        .fadeIn('fast')
        .delay(3000)
        .fadeOut('fast')
        .queue(function(next) {
            $(this).remove();
            next();
        }).appendTo('body');

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
                App.message('Please connect to the internet first.', 'message_error');
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
        this.current_question.answer.forEach(function(resp) {
            console.log('response', resp);
        });

        // Are you required?
        if (this.current_question.logic.required && (first_response === null)) {
            App.message('Survey requires this question to be completed.', 'message_error');
            return;
        }

        // Is the only response and empty is other response?
        if (first_is_type_exception && !first_response) {
            App.message('Please provide a reason before moving on.', 'message_error');
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
        compiledHTML = widgetTemplate({question: question, start_loc: App.start_loc});
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

Survey.prototype.submit = function() {
    var self = this;
    var answers = {};

    // Save answers locally 
    _.each(self.questions, function(question) {
        answers[question.question_id] = question.answer;
    });

    localStorage[self.id] = JSON.stringify(answers);

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

            if (response == null) { 
                return;
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
            App.message('Saving failed, No questions answer in Survey!', 'message_error');
            App.splash();
      }, 1000);
      return;
    } 

    // Save Revisit data 
    localStorage.setItem("facilities", 
            JSON.stringify(App.facilities));

    localStorage.setItem("unsynced_facilities", 
            JSON.stringify(App.unsynced_facilities));

    // Save Submission data
    App.unsynced.push(data);
    var unsynced = JSON.parse(localStorage.unsynced); 
    console.log(unsynced);
    unsynced[self.id] = App.unsynced;
    console.log(unsynced);
    localStorage['unsynced'] = JSON.stringify(unsynced);
    console.log('localStorage', localStorage.unsynced);

    App.message('Saved Submission!', 'message_success');
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
            console.log('value recieved', ans_ind, this.value);
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
        //footer.addClass('bar-footer-super-extended');
        footer.animate({height:220},200).addClass('bar-footer-super-extended');

        //Add overlay
        $('.overlay').fadeIn('fast');

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
            //XXX: Doesn't work with chrome date picker
            val = Date.parse(answer);
            if (isNaN(val)) {
                val = null;
            } else {
                val = (new Date(val)).toISOString();
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
    this._input(question, page, footer, "date_XXX"); //XXX: Fix validation
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

Widgets._getMap = function() {

    var map = L.map('map', {
            center: [App.start_loc.lat, App.start_loc.lon],
            dragging: true,
            maxZoom: 18,
            minZoom: 11,
            zoom: 14,
            zoomControl: false,
            doubleClickZoom: false,
            attributionControl: false
        });
    
    var tile_layer =  new L.tileLayer(App.tile_url, {
        maxZoom: 18,
        useCache: true
    });

    tile_layer.on('tilecachehit',function(ev){
        //console.log('Cache hit: ', ev.url);
    });

    tile_layer.on('tilecachemiss',function(ev){
        //console.log('Cache miss: ', ev.url);
    });

    // Blinking location indicator
    var circle = L.circle(App.start_loc, 5, {
            color: 'red',
            fillColor: '#f00',
            fillOpacity: 0.5,
            zIndexOffset: 777,
    })
        .addTo(map);

    map.circle = circle;

    ///TODO: Replace this with CSSSSSSSssss
    var counter = 0;
    function updateColour() {
        var fillcol = Number((counter % 16)).toString(16);
        var col = Number((counter++ % 13)).toString(16);
        circle.setStyle({
            fillColor : "#f" + fillcol + fillcol,
            color : "#f" + col + col,
        });
    }

    // Save the interval id, clear it every time a page is rendered
    Widgets.interval = window.setInterval(updateColour, 50); // XXX: could be CSS
    
    map.addLayer(tile_layer);
    return map;
};

Widgets.location = function(question, page, footer) {
    // generic setup
    this._input(question, page, footer, "location");

    var self = this;
    var response = $(page).find('.text_input').last().val();
    response = self._validate('location', response, question.logic);
    App.start_loc = response || App.start_loc;

    var map = this._getMap(); 
    map.on('drag', function() {
        map.circle.setLatLng(map.getCenter());
        updateLocation([map.getCenter().lng, map.getCenter().lat]);
    });

    function updateLocation(coords) {
        // Find current length of inputs and update the last one;
        var questions_len = $(page).find('.text_input').length;

        // update array val
        question.answer[questions_len - 1] = {
            response: {'lon': coords[0], 'lat': coords[1]},
            is_type_exception: false,
            metadata: {},
        }
            
        // update latest lon/lat values
        var questions_len = $(page).find('.text_input').length;
        $(page).find('.text_input')
            .last().val(coords[1] + " " + coords[0]);
    }

    $(page)
        .find('.question__find__btn')
        .click(function() {
            App.message('Searching ...', 'message_warning');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var coords = [
                        position.coords.longitude, 
                        position.coords.latitude
                    ];

                    // Set map view and update indicator position
                    //map.setMaxBounds(null);
                    map.setView([coords[1], coords[0]]);
                    map.circle.setLatLng([coords[1], coords[0]]);
                    //map.setMaxBounds(map.getBounds().pad(1));

                    updateLocation(coords); //XXX: DONT MOVE ON

                }, function error() {
                    //If cannot Get location" for some reason,
                    App.message('Could not get your location, please make sure your GPS device is active.',
                            'message_error');
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });

    // disable default event
    $(page)
        .find('.text_input')
        .off('keyup');
};

// Similar to location however you cannot just add location, 
Widgets.facility = function(question, page, footer) {
    var ans = question.answer[0]; // Facility questions only ever have one response
    var lat = ans && ans.response.lat || App.start_loc.lat;
    var lng = ans && ans.response.lon || App.start_loc.lon;

    App.start_loc = {'lat': lat, 'lon': lng};

    /* Buld inital state */
    var map = this._getMap(); 
    map.on('drag', function() {
        map.circle.setLatLng(map.getCenter());
    });

    $(page).find('.facility__name').attr('disabled', true);
    $(page).find('.facility__type').attr('disabled', true);

    // Know which marker is currently "up" 
    var touchedMarker = null;
    // Added facility  
    var addedMarker = null;
    // Add markers here so clearing them isn't such a huge pain
    var facilities_group = new L.featureGroup();
    var new_facilities_group = new L.featureGroup();

    facilities_group.addTo(map);
    new_facilities_group.addTo(map);

    // Revisit API Call calls facilitiesCallback
    reloadFacilities(App.start_loc.lat, App.start_loc.lon);

    /* Helper functions for updates  */
    function reloadFacilities(lat, lon) {
        if (navigator.onLine) {
            // Refresh if possible
            getNearbyFacilities(lat, lon, 
                    FAC_RAD, // Radius in km 
                    NUM_FAC, // limit
                    drawFacilities // what to do with facilities
                );

        } else {
            drawFacilities(App.facilities); // Otherwise draw our synced facilities
        }
    }

    // handles calling drawPoint gets called once per getNearby call 
    function drawFacilities(facilities) {
        var ans = question.answer[0];
        var selected = ans && ans.response.id || null;

        // SYNCED FACILITIES
        facilities_group.clearLayers(); // Clears synced facilities only
        facilities = facilities || [];
        for (var i = 0; i < facilities.length; i++) {
            var facility = facilities[i];

            //if ((facility.coordinates[1] < top_y && facility.coordinates[1] > bot_y)
            //&& (facility.coordinates[0] < top_x && facility.coordinates[0] > bot_x)) {
                var marker = drawPoint(facility.coordinates[1], 
                            facility.coordinates[0], 
                            facility.name, 
                            facility.properties.sector,
                            facility.uuid,
                            onFacilityClick);

                // If selected uuid was from Revisit, paint it white
                if (selected === marker.uuid) {
                    selectFacility(marker);
                }

                facilities_group.addLayer(marker);
            //}
        }

        // UNSYNCED FACILITIES
        new_facilities_group.clearLayers(); // Clears synced facilities only
        _.map(App.unsynced_facilities, function(facility) {
            //console/g.log("new facility added", facility.name);
            var marker = drawNewPoint(facility.coordinates[1], 
                        facility.coordinates[0], 
                        facility.name, 
                        facility.properties.sector,
                        facility.uuid,
                        onFacilityClick, onFacilityDrag); 
            
            if (selected === marker.uuid) {
                selectFacility(marker);
                $(page).find('.facility__btn').html("Remove New Site");
                //console/g.log("new match", selected);
            } 

            // They added a facility in this question before
            if (question._new_facility === marker.uuid) {
                addedMarker = marker;
                $(page).find('.facility__btn').text("Remove New Site");
            }
            
            new_facilities_group.addLayer(marker);
        });

    } 

    function selectFacility(marker) {
        marker.setZIndexOffset(666); // above 250 so it can't be hidden by hovering over neighbour
        $(page).find('.facility__name').attr('disabled', true);
        $(page).find('.facility__type').attr('disabled', true);

        marker.setIcon(icon_selected);
        if (marker.is_new) { 
            marker.setIcon(icon_added);
            addedMarker = marker;
            $(page).find('.facility__name').attr('disabled', false);
            $(page).find('.facility__type').attr('disabled', false);
        }

        touchedMarker = marker;
        question.answer[0] = {
            response: {
                'id': marker.uuid, 
                'lon': marker._latlng.lng, 
                'lat': marker._latlng.lat
            },
            is_type_exception: false,
            metadata: {
                'facility_name': marker.name,
                'facility_sector': marker.sector
            } 
        }

        $(page).find('.facility__name').val(marker.name);
        $(page).find('.facility__type').val(marker.sector);
    }

    function deselectFacility() {
        if (touchedMarker) {
            touchedMarker.setIcon(getIcon(touchedMarker.sector, touchedMarker.is_new));
            touchedMarker.setZIndexOffset(0);
        }

        question.answer = [];
        $(page).find('.facility__name').val("");
        $(page).find('.facility__type').val("other");
        touchedMarker = null;
    }

    function onFacilityClick(e) {
        // Update marker so it looks selected
        var marker = e.target;
        deselectFacility();
        selectFacility(marker);
    }

    function onFacilityDrag(e) {
        var marker = e.target;
        deselectFacility();
        selectFacility(marker);
        App.unsynced_facilities[marker.uuid].coordinates = [
            marker._latlng.lng, 
            marker._latlng.lat
        ];
    }

    // function to wrap up the new facility code
    function addFacility(lat, lng, uuid) {
        deselectFacility();

        //XXX: Add Popup with bits of info
        var addedMarker = drawNewPoint(lat, lng, 
                "New Facility", "other", uuid, 
                onFacilityClick, onFacilityDrag); 
        
        // We added em before 
        if (App.unsynced_facilities[uuid]) {
            addedMarker.sector = App.unsynced_facilities[uuid].properties.sector;
            addedMarker.name = App.unsynced_facilities[uuid].name;
        }

        selectFacility(addedMarker);
        addedMarker.addTo(new_facilities_group);

        return addedMarker;
    }

    /* Handle events */

    // Find me
    $(page)
        .find('.question__find__btn')
        .click(function() {
            App.message('Searching ...', 'message_warning');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var coords = [position.coords.longitude, position.coords.latitude];

                    // Update map position and set indicator position again
                    //map.setMaxBounds(null);
                    map.setView([coords[1], coords[0]]);
                    map.circle.setLatLng([coords[1], coords[0]]);
                    //map.setMaxBounds(map.getBounds().pad(1));

                    // Revisit api call
                    reloadFacilities(coords[1], coords[0]); 

                }, function error() {
                    App.message('Could not get your location, please make sure your GPS device is active.',
                            'message_error');
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
            // You added on before
            if (addedMarker && addedMarker.uuid === question._new_facility) {
                // Get rid of all traces of it
                delete App.unsynced_facilities[addedMarker.uuid];
                new_facilities_group.removeLayer(addedMarker);

                if (addedMarker === touchedMarker) { 
                    deselectFacility();
                }

                $(page).find('.facility__btn').text("Add New Site");
                $(page).find('.facility__name').attr('disabled', true);
                $(page).find('.facility__type').attr('disabled', true);

                addedMarker = null;
                question._new_facility = null;
                return;
            }

            // Adding new facility
            var lat = map.getCenter().lat;
            var lng = map.getCenter().lng;
            var uuid = objectID(); //XXX: TODO replace this shit with new uuid

            // Record this new facility for Revisit submission
            App.unsynced_facilities[uuid] = {
                'name': 'New Facility', 'uuid': uuid, 
                'properties' : {'sector': 'other'},
                'coordinates' : [lng, lat]
            };

            // Get and place marker
            addedMarker = addFacility(lat, lng, uuid);
            $(page).find('.facility__btn').html("Remove New Site");
            $(page).find('.facility__name').attr('disabled', false);
            $(page).find('.facility__type').attr('disabled', false);
            question._new_facility = uuid; // state to prevent multiple facilities

        });

    // Change name
    $(page)
        .find('.facility__name')
        .keyup(function() {
            //console/g.log(this.value);
            if (addedMarker && addedMarker === touchedMarker) {
                // Update facility info
                App.unsynced_facilities[addedMarker.uuid].name = this.value;
                addedMarker.name = this.value;
            } else if (touchedMarker) {
                // Prevent updates for now
                selectFacility(touchedMarker);
            }
        });

    // Change type
    $(page)
        .find('.facility__type')
        .change(function() {
            //console/g.log(this.value);
            if (addedMarker && addedMarker === touchedMarker) {
                // Update facility info
                App.unsynced_facilities[addedMarker.uuid].properties.sector = this.value;
                addedMarker.sector = this.value;
            } else if (touchedMarker) {
                // Prevent updates for now
                selectFacility(touchedMarker);
            }
        });
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
            localStorage.setItem("facilities", JSON.stringify(data.facilities));
            if (cb) {
                //XXX REMEMMERNBE
                App.facilities = data.facilities;
                cb(data.facilities); //drawFacillities callback probs
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
            App.message('Facility Added!', 'message_success');

            // If posted, we don't an unsynced reference to it anymore
            delete App.unsynced_facilities[facility.uuid];
            App.facilities.push(facility);
        },
        
        headers: {
            "Authorization": "Basic " + btoa("dokomoforms" + ":" + "password")
                //DONT DO THIS XXX XXX
        },

        error: function() {
            App.message('Facility submission failed, will try again later.', 'message_error');
        },
        
        complete: function() {
            // Add it into facilities array so it can be selected later
            localStorage.setItem("facilities", 
                    JSON.stringify(App.facilities));

            localStorage.setItem("unsynced_facilities", 
                    JSON.stringify(App.unsynced_facilities));

        }
    });
}

var icon_edu = new L.icon({iconUrl: "/static/img/icons/normal_education.png",iconAnchor: [13, 31]});
var icon_health = new L.icon({iconUrl: "/static/img/icons/normal_health.png", iconAnchor: [13, 31]});
var icon_water = new L.icon({iconUrl: "/static/img/icons/normal_water.png", iconAnchor: [13, 31]});

var icon_new_edu = new L.icon({iconUrl: "/static/img/icons/unsynced_education.png",iconAnchor: [13, 31]});
var icon_new_health = new L.icon({iconUrl: "/static/img/icons/unsynced_health.png", iconAnchor: [13, 31]});
var icon_new_water = new L.icon({iconUrl: "/static/img/icons/unsynced_water.png", iconAnchor: [13, 31]});

var icon_base = new L.icon({iconUrl: "/static/img/icons/normal_base.png", iconAnchor: [13, 31]});
var icon_new_base = new L.icon({iconUrl: "/static/img/icons/unsynced_base.png", iconAnchor: [13, 31]});
var icon_selected = new L.icon({iconUrl: "/static/img/icons/selected-point.png", iconAnchor: [16.2, 48]});
var icon_added = new L.icon({iconUrl: "/static/img/icons/added-point.png", iconAnchor: [16.2, 48]});

var icon_types = {
    "education" : icon_edu,
    "new_education" : icon_new_edu,
    "water" : icon_water,
    "new_water" : icon_new_water,
    "health" : icon_health,
    "new_health" : icon_new_health,
    "base" : icon_base,
    "new_base" : icon_new_base,
};

function getIcon(sector, isNew) {
    var base = "base";
    if (isNew) {
        sector = "new_" + sector;
        base = "new_" + base;
    }
    return icon_types[sector] || icon_types[base];
}

function drawPoint(lat, lng, name, type, uuid, clickEvent) {
    var marker = new L.marker([lat, lng], {
        title: name,
        alt: name,
        clickable: true,
        riseOnHover: true
    });

    marker.uuid = uuid; // store the uuid so we can read it back in the event handler
    marker.sector = type;
    marker.name = name;
    marker.is_new = false;

    marker.options.icon = getIcon(type, marker.is_new);

    marker.on('click', clickEvent);
    return marker;
    
}

function drawNewPoint(lat, lng, name, type, uuid, clickEvent, dragEvent) {
    var marker = new L.marker([lat, lng], {
        title: name,
        alt: name,
        clickable: true,
        draggable: true, //XXX This right here is why i gotta seperate draws
        riseOnHover: true
    });

    marker.uuid = uuid; // store the uuid so we can read it back in the event handler
    marker.sector = type;
    marker.name = name;
    marker.is_new = true;

    marker.options.icon = getIcon(type, marker.is_new);

    marker.on('click', clickEvent);
    marker.on('dragend', dragEvent);
    return marker;
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
