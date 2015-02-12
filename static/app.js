var NEXT = 1;
var PREV = -1;

var App = {
    unsynced: [], // unsynced surveys
    facilities: [], // revisit facilities
    unsynced_facilities: {}, // new facilities
    start_loc: [40.8138912, -73.9624327], 
    submitter_name: ''
   // defaults to nyc, updated by metadata and answers to location questions
};

App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, survey.questions, survey.metadata);
    self.start_loc = survey.metadata.location || self.start_loc;
    self.facilities = JSON.parse(localStorage.facilities || "[]");
    self.submitter_name = localStorage.name;

    if (App.facilities.length === 0) {
        // See if you can get some facilities
        getNearbyFacilities(App.start_loc[0], App.start_loc[1], 
                5, // Radius in km 
                100, // limit
                "facilities", // id for localStorage
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

function Survey(id, questions, metadata) {
    var self = this;
    this.id = id;
    this.questions = questions;
    this.metadata = metadata;

    // Load answers from localStorage
    var answers = JSON.parse(localStorage[this.id] || '{}');
    console.log(answers);
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
    

    console.log(questions);

    // Page navigation
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? PREV : NEXT;
        self.next(offset);
        return false;
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
// XXX: function name doesnt match return types
Survey.prototype.getFirstResponse = function(question) {
    for (var i = 0; i < question.answer.length; i++) {
        if (Widgets._validate(question.type_constraint_name, question.answer[i]) !== null) {
            return question.answer[i];
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
    
    var index = question ? question.sequence_number : this.questions.length + 1;

    if (question) {
        // Show widget
        var widgetHTML = $('#widget_' + question.type_constraint_name).html();
        var widgetTemplate = _.template(widgetHTML);
        var compiledHTML = widgetTemplate({question: question, start_loc: App.start_loc});
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
        var widgetHTML = $('#template_submit').html();
        var widgetTemplate = _.template(widgetHTML);
        var compiledHTML = widgetTemplate({name: App.submitter_name});

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
    
    // Clear any interval events
    if (Widgets.interval) {
        window.clearInterval(Widgets.interval);
        Widgets.interval = null;
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
        console.log('q', q);
        q.answer.forEach(function(ans, ind) {
            var is_other_val = q.is_other || false;

            if (typeof q.is_other === 'object') { 
                is_other_val = q.is_other[ind];
            }

            if (!ans && ans !== 0) {
                return;
            }

            survey_answers.push({
                question_id: q.question_id,
                answer: ans,
                is_other: is_other_val 
            });
        });
    });

    // Post to Revisit 
    localStorage.setItem("facilities", 
            JSON.stringify(App.facilities));

    localStorage.setItem("unsynced_facilities", 
            JSON.stringify(App.unsynced_facilities));

    console.log('revisit-ing', App.unsynced_facilities);
    _.map(App.unsynced_facilities, function(facility) {
        postNewFacility(facility); 
    });

    var data = {
        submitter: App.submitter_name || "anon",
        survey_id: self.id,
        answers: survey_answers
    };

    console.log('submission:', data);

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

    $(page)
        .find('input')
        .change(function() {
            var ans_ind = $(page).find('input').index(this); 
            question.answer[ans_ind] = self._validate(type, this.value);
        });

    // Click the + for new input
    $(page)
        .find('.next_input')
        .click(function() { 
            self._addNewInput(page, $(page).find('input').last(), question);
        });
};

// Handle creating multiple inputs for widgets that support it 
Widgets._addNewInput = function(page, input, question) {
    if (question.allow_multiple) {
        input
            .clone(true)
            .val(null)
            .insertBefore(page.find(".next_input"))
            .focus();
    }
};

// Basic input validation
Widgets._validate = function(type, answer) {
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
              val = answer;
              break;
        case "text":
              if (answer) {
                  val = answer;
              }
              break;
        default:
              //XXX: Others aren't validated the same
              val = answer;
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

    // record values for each select option to update answer array in consistent way
    var $children = []; //XXX: Using question.choices is not enough
    $(page).find('select').children().each(function(i, child){ 
        $children.push(child.value);
    });

    // handle change for text field
    var $other = $(page)
        .find('.text_input')
        .keyup(function() {
            question.answer[$children.length - 1 - 1] = self._validate("text", this.value);
        });


    $other.hide();

    $(page)
        .find('select')
        .change(function() {
            // any change => answer is reset
            question.answer = [];
            question.is_other = [];
            $other.hide();

            // jquery is dumb and inconsistent 
            var svals = $('select').val();
            svals = typeof svals === 'string' ? [svals] : svals;
            // find all select options
            svals.forEach(function(opt) { 
                // Please choose something option wipes answers
                var ind = $children.indexOf(opt) - 1;
                if (opt === 'null') { 
                    return;
                }

                // Default, fill in values (other will be overwritten below if selected)
                question.answer[ind] = opt;
                question.is_other[ind] = false;

                if (opt === 'other') {
                    // Choice is text input
                    question.answer[ind] = $other.val();
                    question.is_other[ind] = true;
                    $other.show();
                } 

             });

            // Toggle off other if deselected on change event 
            if (svals.indexOf('other') < 0) { 
                $other.hide();
            }
            
        });

    // Selection is handled in _template however toggling of view is done here
    question.is_other =  question.is_other || [];
    if (question.answer[question.choices.length] || 
            question.answer[question.choices.length] === '') {
        question.is_other[question.choices.length] = true;
        $other.show();
    }
};

Widgets._getMap = function() {
    var map = L.map('map', {
            center: App.start_loc,
            dragging: true,
            zoom: 13,
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

    return map;
};

Widgets.location = function(question, page) {
    // Map
    var lat = $(page).find('.question__lat').last().val() || App.start_loc[0];
    var lng = $(page).find('.question__lon').last().val() || App.start_loc[1];

    App.start_loc = [lat, lng];

    var map = this._getMap(); 
    map.on('drag', function() {
        map.circle.setLatLng(map.getCenter());
        updateLocation([map.getCenter().lng, map.getCenter().lat]);
    });

    function updateLocation(coords) {
        //XXX: Control which element is updated

        // Find current length of inputs and update the last one;
        var questions_len = $(page).find('.question__location').length;

        // update array val
        question.answer[questions_len - 1] = coords;
            
        // update latest lon/lat values
        $(page).find('.question__lon').last().val(coords[0]);
        $(page).find('.question__lat').last().val(coords[1]);
    }

    $(page)
        .find('.question__btn')
        .click(function() {
            var sync = $('.nav__sync')[0];
            sync.classList.add('icon--spin');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    sync.classList.remove('icon--spin');

                    // Server accepts [lon, lat]
                    var coords = [
                        position.coords.longitude, 
                        position.coords.latitude
                    ];

                    // Set map view and update indicator position
                    map.setView([coords[1], coords[0]]);
                    map.circle
                        .setLatLng([coords[1], coords[0]]);

                    // If allow multiple is set add there exists > 1 divs 
                    if (question.allow_multiple && 
                            typeof question.answer[0] !== "undefined") {
                        $(page)
                            .find('.question__location')
                            .clone()
                            .insertBefore(".question__btn");
                    }

                    updateLocation(coords);

                }, function error() {
                    //TODO: If cannot Get location" for some reason, 
                    sync.classList.remove('icon--spin');
                    alert('error'); //XXX Replace with our message thing
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });
};

// Similar to location however you cannot just add location, 
Widgets.facility = function(question, page) {
    // Map
    var lat = question.answer[0] && question.answer[0][1][1] || App.start_loc[0];
    var lng = question.answer[0] && question.answer[0][1][0] || App.start_loc[1];

    App.start_loc = [lat, lng];

    /* Buld inital state */
    var map = this._getMap(); 
    map.on('drag', function() {
        map.circle.setLatLng(map.getCenter());
    });

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
    if (navigator.onLine) {
        // Refresh if possible
        getNearbyFacilities(App.start_loc[0], App.start_loc[1], 
                5, // Radius in km 
                100, // limit
                "facilities", // id for localStorage
                drawFacilities // what to do with facilities
            );

    } else {
        drawFacilities(App.facilities); // Otherwise draw our synced facilities
    }

    /* Helper functions for updates  */

    // handles calling drawPoint gets called once per getNearby call 
    function drawFacilities(facilities) {
        var selected = question.answer[0] && question.answer[0][0] || null;

        // SYNCED FACILITIES
        facilities_group.clearLayers(); // Clears synced facilities only
        facilities = facilities || [];
        for (var i = 0; i < facilities.length; i++) {
            var facility = facilities[i];
            var marker = drawPoint(facility.coordinates[1], 
                        facility.coordinates[0], 
                        facility.name, 
                        facility.properties.sector,
                        facility.uuid,
                        onFacilityClick);

            // If selected uuid was from Revisit, paint it white
            if (selected === marker.uuid) {
                selectFacility(marker);
                console.log("match", selected);
            }

            facilities_group.addLayer(marker);
        }

        // UNSYNCED FACILITIES
        new_facilities_group.clearLayers(); // Clears synced facilities only
        _.map(App.unsynced_facilities, function(facility) {
            console.log("new facility added", facility.name);
            var marker = drawNewPoint(facility.coordinates[1], 
                        facility.coordinates[0], 
                        facility.name, 
                        facility.properties.sector,
                        facility.uuid,
                        onFacilityClick, onFacilityDrag); 
            
            if (selected === marker.uuid) {
                selectFacility(marker);
                $(page).find('.facility__btn').html("Remove New Site");
                console.log("new match", selected);
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
        marker.setIcon(icon_selected);
        if (marker.is_new) { 
            marker.setIcon(icon_added);
            addedMarker = marker;
        }

        touchedMarker = marker;
        question.answer[0] = [marker.uuid, [marker._latlng.lng, marker._latlng.lat]];
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
        .find('.find__btn')
        .click(function() {
            var sync = $('.nav__sync')[0];
            sync.classList.add('icon--spin');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var coords = [position.coords.longitude, position.coords.latitude];

                    // Update map position and set indicator position again
                    map.setView([coords[1], coords[0]]);
                    map.circle
                        .setLatLng([coords[1], coords[0]]);

                    // Revisit api call
                    if (navigator.onLine) {
                        // refresh if possible
                        getNearbyFacilities(coords[1], coords[0],
                                5, // Radius in km 
                                100, // limit
                                "facilities", // id for localStorage
                                drawFacilities// what to do with facilities
                        );
                    }

                    sync.classList.remove('icon--spin');
                }, function error() {
                    sync.classList.remove('icon--spin');
                    alert('error'); ///XXX: DONT FORGET MEMEE
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
                'coordinates' : [lng, lat],
                'question_id' : question.question_id // XXX: Remove this from here
            };

            // Get and place marker
            addedMarker = addFacility(lat, lng, uuid);
            $(page).find('.facility__btn').html("Remove New Site");
            question._new_facility = uuid; // state to prevent multiple facilities

        });

    // Change name
    $(page)
        .find('.facility__name')
        .keyup(function() {
            console.log(this.value);
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
            console.log(this.value);
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
function getNearbyFacilities(lat, lng, rad, lim, id, cb) {
    //var url = "http://staging.revisit.global/api/v0/facilities.json" 
    var url = "http://localhost:3000/api/v0/facilities.json"; // install revisit server from git
    // Revisit ajax req
    console.log("MADE EXTERNAL REVISIT QUERY");
    $.get(url,{
            near: lat + "," + lng,
            rad: rad,
            limit: lim,
            sortDesc: "updatedAt",
            fields: "name,uuid,coordinates,properties:sector", //filters results to include just those three fields,
        },
        function(data) {
            localStorage.setItem(id, JSON.stringify(data.facilities));
            if (cb) {
                App.facilities = data.facilities;
                cb(data.facilities);
            }
        }
    );
}

// XXX: Really doesn't need to
function postNewFacility(facility) {
    var url = "http://staging.revisit.global/api/v0/facilities.json";
    //var url = "http://localhost:3000/api/v0/facilities.json" // install revisit server from git

    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(facility),
        dataType: 'json',
        success: function() {
            App.message('Facility Added!');

            // If posted, we don't an unsynced reference to it anymore
            delete App.unsynced_facilities[facility.uuid];
            App.facilities.push(facility);
        },
        
        error: function() {
            App.message('Facility submission failed, will try again later.');
            //TODO: Way to resync on failure like submissions
        },
        
        complete: function() {
            //TODO get these unsynced facilities to be drawn after map refresh?
            
            // Add it into facilities array so it can be selected later
            console.log('storing it all');
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
var icon_selected = new L.icon({iconUrl: "/static/img/icons/selected-point.png", iconAnchor: [15, 48]});
var icon_added = new L.icon({iconUrl: "/static/img/icons/added-point.png", iconAnchor: [15, 48]});

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
