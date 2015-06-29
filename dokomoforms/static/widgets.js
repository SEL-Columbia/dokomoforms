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

    // Clean up answer array, short circuits on is_type_exception responses
    self._orderAnswerArray(question, page, footer, type);

    // Set up input event listner
    $(page)
        .find('.text_input')
        .keyup(function() { //XXX: Change isn't sensitive enough on safari?
            var ans_ind = $(page).find('input').index(this); 
            question.answer[ans_ind] = { 
                response: self._validate(type, this.value, question.logic),
                is_type_exception: false,
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
                is_type_exception: false,
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
                is_type_exception: true,
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
                    is_type_exception: true,
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
                is_type_exception: true,
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
 * Time Widget
 *
 * @question: question data
 * @page: the widget container DOM element
 * @footer: footer container DOM element
 */
Widgets.time = function(question, page, footer) {
    //XXX: TODO change input thing to be jquery-ey
    this._input(question, page, footer, "time"); //XXX: Fix validation
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
        choices[ind] = choice.question_choice_id;
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

        });

    // Selection is handled in _template however toggling of view is done here
    var response = question.answer[question.choices.length];
    if (response 
            && response.is_type_exception 
            && response.metadata.type_exception === 'other') {
        $other.show();
    }
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

exports.Widgets = Widgets; 
