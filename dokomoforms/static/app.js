var NEXT = 1;
var PREV = -1;
var ON = 1;
var OFF = 0;
var NUM_FAC = 256;
var FAC_RAD = 2; //in KM

var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    start_loc: {'lat': 40.8138912, 'lon': -73.9624327}, 
    submitter_name: ''
   // defaults to nyc, updated by metadata and answers to location questions
};

App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, survey.survey_version, survey.questions, survey.survey_metadata);
    self.start_loc = survey.survey_metadata.location || self.start_loc;
    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name;

    if (App.facilities.length === 0) {
        // See if you can get some facilities
        getNearbyFacilities(App.start_loc.lat, App.start_loc.lon, 
            FAC_RAD, // Radius in km 
            NUM_FAC, // limit
            null// what to do with facilities
        );
    }

    // Load up any unsynced facilities
    App.unsynced_facilities = 
        JSON.parse(localStorage.unsynced_facilities || "{}");

    // Manual sync    
    $('.nav__sync')
        .click(function() {
            self.sync();
        });
        
    // Syncing intervals
    setInterval(App.sync, 10000);
    
    // AppCache updates
    //window.applicationCache.addEventListener('updateready', function() {
    //    alert('app updated, reloading...');
    //    window.location.reload();
    //});
};

App.sync = function() {
    if (navigator.onLine && App.unsynced.length) {
        _.each(App.unsynced, function(survey) {
            survey.submit();
        });
        App.unsynced = []; //XXX: Surveys can fail again, better to pop unsuccess;
    }
};

App.message = function(text) {
    // Shows a message to user
    // E.g. "Your survey has been submitted"
    $('.message')
        .clearQueue()
        .text(text)
        .fadeIn('fast')
        .delay(3000)
        .fadeOut('fast');
};

// Handle caching map layer
App._getMapLayer = function() {
    //XXX: TODO: Some how cache this on survey load 
    function getImage(url, cb) {
        // Retrieves an image from cache, possibly fetching it first
        var imgKey = url.split('.').slice(1).join('.').replace(/\//g, '');
        var img = localStorage[imgKey];
        if (img) {
            cb(img);
        } else {
            imgToBase64(url, 'image/png', function(img) {
                localStorage[imgKey] = img;
                cb(img);
            });
        }
    }
    
    function imgToBase64(url, outputFormat, callback){
        var canvas = document.createElement('canvas'),
            ctx = canvas.getContext('2d'),
            img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = function(){
            var dataURL;
            canvas.height = img.height;
            canvas.width = img.width;
            ctx.drawImage(img, 0, 0);
            dataURL = canvas.toDataURL(outputFormat);
            callback.call(this, dataURL);
            canvas = null; 
        };
        img.src = url;
    }

    // Tile layer
    return new L.TileLayer.Functional(function(view) {
        var deferred = $.Deferred();
        var url = 'http://{s}.tiles.mapbox.com/v3/examples.map-20v6611k/{z}/{y}/{x}.png'
            .replace('{s}', 'abcd'[Math.round(Math.random() * 3)])
            .replace('{z}', Math.floor(view.zoom))
            .replace('{x}', view.tile.row)
            .replace('{y}', view.tile.column);
        getImage(url, deferred.resolve);
        return deferred.promise();
    });

};

function Survey(id, version, questions, metadata) {
    var self = this;
    this.id = id;
    this.questions = questions;
    this.metadata = metadata;
    this.version = version;

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

    // Now that you know order, you can set prev pointers
    var curr_q = self.current_question;
    var prev_q = null;
    do {
        curr_q.prev = prev_q;
        prev_q = curr_q;
        curr_q = curr_q.next;
    } while (curr_q);
    

    //console/g.log(questions);

    // Page navigation
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? PREV : NEXT;
        self.next(offset);
    });
    
    // Render first question
    self.render(self.current_question);
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
// XXX: function name doesnt match return types or what its doing
Survey.prototype.getFirstResponse = function(question) {
    for (var i = 0; i < question.answer.length; i++) {
        var answer = question.answer[i];
        if (answer && typeof answer.response !== 'undefined') {
            return answer.response
        }
    }

    return null;
};

// Choose next question, deals with branching and back/forth movement
Survey.prototype.next = function(offset) {
    var self = this;
    var next_question = offset === PREV ? this.current_question.prev : this.current_question.next;
    var index = $('.content').data('index');
    var first_response = this.getFirstResponse(this.current_question); 

    //XXX: 0 is not the indicator anymore its lowest sequence num;
    if (index === self.lowest_sequence_number && offset === PREV) {
        // Going backwards on first q is a no-no;
        return;
    }

    if (index === this.questions.length + 1 && offset === PREV) {
        // Going backwards at submit means render ME;
        next_question = this.current_question;
    } 
    
    if (offset === NEXT) {
        if (this.current_question.logic.required && (first_response === null)) {
            App.message('Survey requires this question to be completed.');
            return;
        }

        var other_response = this.current_question.answer && this.current_question.answer[0]; // I know its position always
        if (other_response && other_response.is_other && !other_response.response) {
            App.message('Please provide a reason before moving on.');
            return;
        }

        // Check if question was a branching question
        if (this.current_question.branches && first_response) {
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
    var content = $('.content');
    
    var widgetHTML;
    var widgetTemplate;
    var compiledHTML;
    
    var index = question ? question.sequence_number : this.questions.length + 1;

    // Clear any interval events
    if (Widgets.interval) {
        window.clearInterval(Widgets.interval);
        Widgets.interval = null;
    }

    if (question) {
        // Show widget
        widgetHTML = $('#widget_' + question.type_constraint_name).html();
        widgetTemplate = _.template(widgetHTML);
        compiledHTML = widgetTemplate({question: question, start_loc: App.start_loc});
        self.current_question = question;

        // Render question
        content.empty()
            .data('index', index)
            .html(compiledHTML)
            .scrollTop(); //XXX: Ignored in chrome ...
        
        // Attach widget events
        Widgets[question.type_constraint_name](question, content);

    } else {
        // Show submit page
        widgetHTML = $('#template_submit').html();
        widgetTemplate = _.template(widgetHTML);
        compiledHTML = widgetTemplate({name: App.submitter_name});

        content.empty()
            .data('index', index)
            .html(compiledHTML)
            .find('.question__btn')
                .one('click', function() {
                    self.submit();
                });
        content
            .find('.name_input')
            .keyup(function() {
                App.submitter_name = this.value;
                localStorage.name = App.submitter_name;
            });
    }
    
    // Update nav
    $('.page_nav__progress')
        .text((index) + ' / ' + (this.questions.length + 1));
};

Survey.prototype.submit = function() {
    var self = this;
    var sync = $('.nav__sync')[0];
    var save_btn = $('.question__saving')[0];
    var answers = {};

    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    
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
            var response =  ans.response;
            var is_other = ans.is_other || false;
            var metadata = ans.metadata || null;

            if (typeof response === undefined) { 
                return;
            }

            survey_answers.push({
                question_id: q.question_id,
                answer: response,
                answer_metadata: metadata,
                is_other: is_other
            });

        });
    });

    // Post to Revisit 
    localStorage.setItem("facilities", 
            JSON.stringify(App.facilities));

    localStorage.setItem("unsynced_facilities", 
            JSON.stringify(App.unsynced_facilities));

    //console.log('revisit-ing', App.unsynced_facilities);
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });

    var data = {
        submitter: App.submitter_name || "anon",
        survey_id: self.id,
        answers: survey_answers
    };

    //console.log('submission:', data);

    sync.classList.add('icon--spin');
    save_btn.classList.add('icon--spin');
    
    // Don't post with no replies
    if (JSON.stringify(survey_answers) === '[]') {
      // Not doing instantly to make it seem like App tried reaaall hard
      setTimeout(function() {
        sync.classList.remove('icon--spin');
        save_btn.classList.remove('icon--spin');
        App.message('Submission failed, No questions answer in Survey!');
        self.render(self.questions[0]);
      }, 1000);
      return;
    }

    $.ajax({
        url: '',
        type: 'POST',
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(data),
        headers: {
            "X-XSRFToken": getCookie("_xsrf")
        },
        dataType: 'json',
        success: function() {
            App.message('Survey submitted!');
        },
        error: function() {
            App.message('Submission failed, will try again later.');
            App.unsynced.push(self);
        },
        complete: function() {
            setTimeout(function() {
                save_btn.classList.remove('icon--spin');
                sync.classList.remove('icon--spin');
                self.render(self.questions[0]);
            }, 1000);
        }
    });
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
//      location
//      note
//
// All widgets store results in the questions.answer array
Widgets._input = function(question, page, type) {
    var self = this;
    self.state = OFF;
    //console.log("Initial question ans array", question.answer);
    
    // Render add/minus input buttons 
    Widgets._renderRepeat(page, question);

    //Render don't know
    Widgets._renderOther(page, question, self);

    // Clean up answer array, short circuits on is_other responses
    question.answer = []; //XXX: Must be reinit'd to prevent sparse array problems
    $(page).find('input').each(function(i, child) { 
        if ((child.className.indexOf('other_input') > - 1) && !child.disabled) {
            // if don't know input field has a response, break 
            question.answer = [{
                response: self._validate('text', child.value, question.logic),
                is_other: true
            }];

            return false;
        }

        if ((child.className.indexOf('other_input') === -1) && child.value !== "") {
            // Ignore other responses if they don't short circut the loop above
            question.answer[i] = {
                response: self._validate(type, child.value, question.logic),
                is_other: false
            }
        }
    });

    //console.log('Restored question ans array', question.answer);
    
    // Set up input event listner
    $(page)
        .find('.text_input').not('.other_input')
        .change(function() { //XXX: Change isn't sensitive enough on safari?
            var ans_ind = $(page).find('input').index(this); 
            question.answer[ans_ind] = { 
                response: self._validate(type, this.value, question.logic),
                is_other: false
            }

        });

    // Click the + for new input
    $(page)
        .find('.question__add')
        .click(function() { 
            self._addNewInput(page, $(page).find('input').not('.other_input').last(), question);

        });

    // Click the - to remove the newest input
    $(page)
        .find('.question__minus')
        .click(function() { 
            self._removeNewestInput($(page).find('input').not('.other_input'), question);

        });
    
    // Click the other button when you don't know answer
    $(page)
        .find('.question__btn__other')
        .click(function() { 
            self.state = (self.state + 1) % 2 // toggle btwn 1 and 0
            self._toggleOther(page, question, self.state);
        });


    // Set up other input event listener
    $(page)
        .find('.other_input')
        .change(function() { //XXX: Change isn't sensitive enough on safari?
            question.answer = [{ 
                response: self._validate('text', this.value, question.logic),
                is_other: true
            }];
        });
};

// Handle creating multiple inputs for widgets that support it 
Widgets._addNewInput = function(page, input, question) {
    if (question.allow_multiple) { //XXX: Technically this btn clickable => allow_multiple 
        input
            .clone(true)
            .val(null)
            .insertAfter(input)
            .focus();
    }
};

Widgets._removeNewestInput = function(inputs, question) {
    if (question.allow_multiple && (inputs.length > 1)) {
        delete question.answer[inputs.length - 1];
        inputs
            .last()
            .remove()
    }

    inputs
        .last()
        .focus()
};

// Render 'don't know' section if question has with_other logic
// Display response and alter widget state if first response is other
Widgets._renderOther = function(page, question, input) {
    var self = this;
    // Render don't know feature 
    if (question.logic.with_other) {
        var repeatHTML = $('#template_other').html();
        var widgetTemplate = _.template(repeatHTML);
        var compiledHTML = widgetTemplate({question: question});
        $(page).append(compiledHTML);

        var other_response = question.answer && question.answer[0] && question.answer[0].is_other;
        if (other_response) {
            // Disable main input
            this._toggleOther(page, question, ON);
            input.state = ON;
        }
    }
}

// Toggle the 'don't know' section based on passed in state value on given page
// Alters question.answer array
Widgets._toggleOther = function(page, question, state) {
    var self = this;
    question.answer = [];
    
    if (state == ON) {

        // Disable regular inputs
        $(page).find('.text_input').not('.other_input').each(function(i, child) { 
                $(child).attr('disabled', true);
        });
        
        $(page).find('.question__other').show();
        
        $(page).find('.other_input').each(function(i, child) { 
            // Doesn't matter if response is there or not
            question.answer[0] = {
                response: self._validate('text', child.value, question.logic),
                is_other: true
            }
        });

        // Enable other input
        $(page).find('.other_input').each(function(i, child) { 
                $(child).attr('disabled', false);
        });

        $('.question__btn__other')[0].classList.add('question__btn__active');

    } else if (state === OFF) { 
    
        // Enable regular inputs
        $(page).find('.text_input').not('.other_input').each(function(i, child) { 
              $(child).attr('disabled', false);
        });
        
        $(page).find('.question__other').hide();
        
        $(page).find('.text_input').not('.other_input').each(function(i, child) { 
            if (child.value !== "") { 
                question.answer[i] = {
                    response: self._validate(question.type_constraint_name, child.value, question.logic),
                    is_other: false
                }
            }
        });
        
        // Disable other input
        $(page).find('.other_input').each(function(i, child) { 
                $(child).attr('disabled', true);
        });

        $('.question__btn__other')[0].classList.remove('question__btn__active');
    }
}

// Render +/- buttons on given page
Widgets._renderRepeat = function(page, question) {
    // Render add/minus input buttons 
    if (question.allow_multiple) {
        var repeatHTML = $('#template_repeat').html();
        var widgetTemplate = _.template(repeatHTML);
        var compiledHTML = widgetTemplate({question: question});
        $(page).append(compiledHTML)
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

Widgets.text = function(question, page) {
    this._input(question, page, "text");
};

Widgets.integer = function(question, page) {
    this._input(question, page, "integer");
};

Widgets.decimal = function(question, page) {
    this._input(question, page, "decimal");
};

Widgets.date = function(question, page) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, "date_XXX"); //XXX: Fix validation
};

Widgets.time = function(question, page) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, "time"); //XXX: Fix validation
};

Widgets.note = function() {
};

// Multiple choice and multiple choice with other are handled here by same func
// XXX: possibly two widgets (multi select and multi choice)
Widgets.multiple_choice = function(question, page) {
    var self = this;

    // array of choice uuids
    var choices = [];
    question.choices.forEach(function(choice, ind) {
        choices[ind] = choice.question_choice_id;
    }); 
    choices[question.choices.length] = "other"; 

    // handle change for text field
    var $other = $(page)
        .find('.text_input')
        .change(function() {
            question.answer[question.choices.length] = { 
                response: self._validate("text", this.value, question.logic),
                is_other: true
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
                    is_other: false
                }

                if (opt === 'other') {
                    question.answer[ind] = {
                        response: $other.val(), // Preserves prev response
                        is_other: true
                    }

                    $other.show();
                } 
             });

            // Toggle off other if deselected on change event 
            if (svals.indexOf('other') < 0) { 
                $other.hide();
            }
            
        });

    // Selection is handled in _template however toggling of view is done here
    if (question.answer[question.choices.length] && 
            question.answer[question.choices.length].is_other &&
                question.answer[question.choices.length].response) {
        $other.show();
    }
};

Widgets._getMap = function() {
    var map = L.map('map', {
            center: [App.start_loc.lat, App.start_loc.lon],
            dragging: true,
            zoom: 13,
            minZoom: 13,
            maxZoom: 14,
            zoomControl: false,
            doubleClickZoom: false,
            attributionControl: false
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

    map.addLayer(App._getMapLayer());
    map.setMaxBounds(map.getBounds().pad(1));
    return map;
};

Widgets.location = function(question, page) {
    var self = this;
    var response = $(page).find('.text_input').not('.other_input').last().val();
    response = self._validate('location', response, question.logic);
    App.start_loc = response || App.start_loc;

    var map = this._getMap(); 
    map.on('drag', function() {
        map.circle.setLatLng(map.getCenter());
        updateLocation([map.getCenter().lng, map.getCenter().lat]);
    });

    // generic setup
    this._input(question, page, "location");

    function updateLocation(coords) {
        // Find current length of inputs and update the last one;
        var questions_len = $(page).find('.text_input').not('.other_input').length;

        // update array val
        question.answer[questions_len - 1] = {
            response: {'lon': coords[0], 'lat': coords[1]},
            is_other: false
        }
            
        // update latest lon/lat values
        var questions_len = $(page).find('.text_input').not('.other_input').length;
        $(page).find('.text_input').not('.other_input')
            .last().val(coords[1] + " " + coords[0]);
    }

    $(page)
        .find('.question__find__btn')
        .click(function() {
            var sync = $('.nav__sync')[0];
            sync.classList.add('icon--spin');
            App.message('Searching ...');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    sync.classList.remove('icon--spin');

                    // Server accepts [lon, lat]
                    var coords = [
                        position.coords.longitude, 
                        position.coords.latitude
                    ];

                    // Set map view and update indicator position
                    map.setMaxBounds(null);
                    map.setView([coords[1], coords[0]]);
                    map.circle.setLatLng([coords[1], coords[0]]);
                    map.setMaxBounds(map.getBounds().pad(1));

                    updateLocation(coords);

                }, function error() {
                    //If cannot Get location" for some reason, 
                    sync.classList.remove('icon--spin');
                    App.message('Could not get your location, please make sure your GPS device is active.');
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });

    // disable default event
    $(page)
        .find('.text_input').not('.other_input')
        .off('change');
};

// Similar to location however you cannot just add location, 
Widgets.facility = function(question, page) {
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
            is_other: false,
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
            var sync = $('.nav__sync')[0];
            sync.classList.add('icon--spin');
            App.message('Searching ...');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var coords = [position.coords.longitude, position.coords.latitude];

                    // Update map position and set indicator position again
                    map.setMaxBounds(null);
                    map.setView([coords[1], coords[0]]);
                    map.circle.setLatLng([coords[1], coords[0]]);
                    map.setMaxBounds(map.getBounds().pad(1));

                    // Revisit api call
                    reloadFacilities(coords[1], coords[0]); 

                    sync.classList.remove('icon--spin');
                }, function error() {
                    sync.classList.remove('icon--spin');
                    App.message('Could not get your location, please make sure your GPS device is active.');
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
            sortDesc: "updatedAt",
            fields: "name,uuid,coordinates,properties:sector", //filters results to include just those three fields,
        },
        function(data) {
            localStorage.setItem("facilities", JSON.stringify(data.facilities));
            if (cb) {
                App.facilities = data.facilities;
                cb(data.facilities); //drawFacillities callback probs
            }
        }
    );
}

// XXX: Really doesn't need to
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
            App.message('Facility Added!');

            // If posted, we don't an unsynced reference to it anymore
            delete App.unsynced_facilities[facility.uuid];
            App.facilities.push(facility);
        },
        
        headers: {
            "Authorization": "Basic " + btoa("dokomoforms" + ":" + "password")
                //DONT DO THIS XXX XXX
        },

        error: function() {
            App.message('Facility submission failed, will try again later.');
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
