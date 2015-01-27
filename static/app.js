var NEXT = 1;
var PREV = -1;

App = {
    unsynced: [], // unsynced surveys
    facilities: {}, // new facilities
    start_loc: [40.8138912, -73.9624327] 
   // defaults to nyc, updated by metadata and answers to location questions
};

App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, survey.questions, survey.metadata);
    self.start_loc = survey.metadata.location || self.start_loc;
    //App.facilities = localStorage['facilities'] || {};

    // Manual sync    
    $('.nav__sync')
        .click(function() {
            self.sync();
        });
        
    // Syncing intervals
    setInterval(App.sync, 10000);
    
    // AppCache updates
    window.applicationCache.addEventListener('updateready', function() {
        alert('app updated, reloading...');
        window.location.reload();
    });
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
    };
    
    function imgToBase64(url, outputFormat, callback){
        var canvas = document.createElement('canvas'),
            ctx = canvas.getContext('2d'),
            img = new Image;
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
    };

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

}

function Survey(id, questions, metadata) {
    var self = this;
    this.id = id;
    this.questions = questions;
    this.metadata = metadata;

    // Load answers from localStorage
    var answers = JSON.parse(localStorage[this.id] || '{}');
    _.each(this.questions, function(question, ind, questions) {
        question.answer = answers[question.question_id] || [];
        // Set next pointers
        question.next = self.getQuestion(question.question_to_sequence_number);
    });

    // No where to start, and number
    this.current_question = this.questions[0];
    this.lowest_sequence_number = this.current_question.sequence_number;

    // Now that you know order, you can set prev pointers
    var curr_q = this.current_question;
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
    this.render(this.current_question);
};

// Search by sequence number instead of array pos
Survey.prototype.getQuestion = function(seq) {
    var self = this;
    for(i = 0; i < self.questions.length; i++) {
        if (self.questions[i].sequence_number === seq)
            return self.questions[i]
    }

    return null;
}

// Answer array may have elements even if answer[0] is undefined
Survey.prototype.getFirstResponse = function(question) {
    for (i = 0; i < question.answer.length; i++) {
        if (question.answer[i]) 
            return question.answer[i];
    }

    return null;
}

// Choose next question, deals with branching and back/forth movement
Survey.prototype.next = function(offset) {
    var self = this;
    var next_question = offset === PREV ? this.current_question.prev : this.current_question.next;
    var index = $('.content').data('index');
    var response = this.current_question.answer;
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
        // XXX: prev_question.answer field is a mess to check, need to purify ans
        if (this.current_question.logic.required 
                && (first_response && first_response !== 0))  {
            App.message('Survey requires this question to be completed.');
            return;
        }

        // Check if question was a branching question
        if (this.current_question.branches && first_response) {
            var branches = this.current_question.branches;
            for (i=0; i < branches.length; i++) {
                if(branches[i].question_choice_id == first_response) {
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
        var templateHTML = $('#widget_' + question.type_constraint_name).html();
        var template = _.template(templateHTML);
        var html = template({question: question});
        
        self.current_question = question;
        // Render question
        content.empty()
            .data('index', index)
            .html(html)
            .scrollTop(); //XXX: Ignored in chrome ...
        
        // Clear any interval events
        if (Widgets.interval) {
            window.clearInterval(Widgets.interval);
            Widgets.interval = null;
        }

        // Attach widget events
        Widgets[question.type_constraint_name](question, content);
    } else {
        // Show submit page
        content.empty()
            .data('index', index)
            .html($('#template_submit').html())
            .find('.question__btn')
                .one('click', function() {
                    self.submit();
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
    var answers = [];
    self.questions.forEach(function(q) {
        console.log('q', q);
        q.answer.forEach(function(ans, ind) {
            var is_other_val = q.is_other || false;

            if (typeof q.is_other === 'object') 
                is_other_val = q.is_other[ind];

            if (!ans && ans !== 0) 
                return;

            answers.push({
                question_id: q.question_id,
                answer: ans,
                is_other: is_other_val 
            });
        });
    });

    // Post to Revisit 
    console.log('revisit-ing', App.facilities);
    _.map(App.facilities, function(facility) {
        postNewFacility(facility); 
    });

    var data = {
        survey_id: self.id,
        answers: answers
    };

    console.log('submission:', data);

    sync.classList.add('icon--spin');
    save_btn.classList.add('icon--spin');
    
    // Don't post with no replies
    if (JSON.stringify(answers) === '[]') {
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
        fail: function() {
            App.message('Submission failed, will try again later.');
            App.unsynced.push(self);
        },
        error: function() {
            App.message('Submission failed, will try again later.');
            App.unsynced.push(self);
        }
    }).done(function() {
        setTimeout(function() {
            save_btn.classList.remove('icon--spin');
            sync.classList.remove('icon--spin');
            self.render(self.questions[0]);
        }, 1000);
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
//
// All widgets store results in the questions.answer array
Widgets.text = function(question, page) {

    var self = this;
    function keyup(e) {
        var ans_ind = ($(page).find('input')).index(this);
        question.answer[ans_ind] = this.value;
        if (e.keyCode === 13) {
            self._addNewInput(page, question, 'text_input', 'text', keyup);
        }
    };

    // Click the + for new input
    $(page)
        .find('.next_input')
        .click(function() { 
            self._addNewInput(page, question, 'text_input', 'text', keyup);
        });

    $(page)
        .find('input')
        .keyup(keyup);
};

Widgets.integer = function(question, page) {
    var self = this;
    function keyup(e) {
        var ans_ind = ($(page).find('input')).index(this);
        question.answer[ans_ind] = parseInt(this.value);
        if (e.keyCode === 13) {
            self._addNewInput(page, question, 'text_input', 'number', keyup);
        }
    };
    
    // Click the + for new input
    $(page)
        .find('.next_input')
        .click(function() { 
            self._addNewInput(page, question, 'text_input', 'number', keyup);
        });

    $(page)
        .find('input')
        .keyup(keyup);
};

Widgets.decimal = function(question, page) {
    var self = this;
    function keyup(e) {
        var ans_ind = ($(page).find('input')).index(this);
        question.answer[ans_ind] = parseFloat(this.value);
        if (e.keyCode === 13) {
            self._addNewInput(page, question, 'text_input', 'number', keyup);
        }
    };

    // Click the + for new input
    $(page)
        .find('.next_input')
        .click(function() { 
            self._addNewInput(page, question, 'text_input', 'number', keyup);
        });

    $(page)
        .find('input')
        .keyup(keyup);
};

// Date and time respond better to change then keypresses
Widgets.date = function(question, page) {
    //XXX: TODO change input thing to be jquery-ey
    var self = this;
    function change() {
        var ans_ind = ($(page).find('input')).index(this);
        if (this.value !== '') 
            question.answer[ans_ind] = this.value;

    };

    function keyup(e) {
        if (e.keyCode === 13) {
            self._addNewInput(page, question, 'text_input', 'date', keyup, change);
        }
    }

    // Click the + for new input
    $(page)
        .find('.next_input')
        .click(function() { 
            self._addNewInput(page, question, 'text_input', 'date', keyup, change);
        });

    $(page)
        .find('input')
        .change(change)
        .keyup(keyup)
};

Widgets.time = function(question, page) {
    //XXX: TODO change input thing to be jquery-ey
    var self = this;
    function change() {
        var ans_ind = ($(page).find('input')).index(this);
        if (this.value !== '') 
            question.answer[ans_ind] = this.value;

    };

    function keyup(e) {
        if (e.keyCode === 13) {
            self._addNewInput(page, question, 'text_input', 'time', keyup, change);
        }
    }

    // Click the + for new input
    $(page)
        .find('.next_input')
        .click(function() { 
            self._addNewInput(page, question, 'text_input', 'time', keyup, change);
        });

    $(page)
        .find('input')
        .change(change)
        .keyup(keyup)
};

Widgets.note = function(question, page) {
};

// Multiple choice and multiple choice with other are handled here by same func
Widgets.multiple_choice = function(question, page) {

    // record values for each select option to update answer array in consistent way
    var $children = [];
    // jquery has own array funcs?
    $(page).find('select').children().each(function(i, child){$children.push(child.value)});

    // handle change for text field
    var $other = $(page)
        .find('.text_input')
        .keyup(function() {
            question.answer[$children.length - 1 - 1] = this.value;
        });

    $other.hide();

    var $select = $(page)
        .find('select')
        .change(function() {
            // any change => answer is reset
            question.answer = [];
            question.is_other = [];
            $other.hide();

            // jquery is dumb and inconsistent 
            var svals = $('select').val();
            svals = typeof svals === 'string' ? [svals] : svals
            // find all select options
            svals.forEach(function(opt) { //TODO: THIS IS INCORRECT LOOP
                // Please choose something option wipes answers
                var ind = $children.indexOf(opt) - 1;
                if (opt === 'null') 
                    return;

                // Default, fill in values (other will be overwritten below if selected)
                question.answer[ind] = opt;
                question.is_other[ind] = false;

                if (opt  == 'other') {
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
                                              // end - default value pos
    if (question.is_other && question.is_other[$children.length - 1 - 1]) {
        //$select.find("#with_other").attr("selected", true);
        $other.show();
    }

};

Widgets.location = function(question, page) {
    // TODO: add location status
    var self = this;
    
    // Map
    var len = question.answer.length - 1;
    var lat = question.answer[len] && question.answer[len][1] || App.start_loc[0];
    var lng = question.answer[len] && question.answer[len][0] || App.start_loc[1];
    App.start_loc = [lat, lng];

    var map = L.map('map', {
            center: App.start_loc,
            dragging: true,
            zoom: 13,
            zoomControl: true,
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
    

    var counter = 0;
    function updateColour() {
        var fillcol = Number((counter % 16)).toString(16);
        var col = Number((counter++ % 13)).toString(16);
        circle.setStyle({
            fillColor : "#f" + fillcol + fillcol,
            color : "#f" + col + col,
        });
    };

    // Save the interval id, clear it every time a page is rendered
    Widgets.interval = window.setInterval(updateColour, 50);
    
    map.addLayer(App._getMapLayer());

    // Location is the only one that doesn't use the same keyup function due to
    // the btn being the only way to input values in the view.
    var loc_div = "<div class='loc_input'><input class='text_input question__lat' type='text'><input class='text_input question__lon' type='text'></div>";

    $(page)
        .find('.question__btn')
        .click(function() {
            var sync = $('.nav__sync')[0];
            sync.classList.add('icon--spin');
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    sync.classList.remove('icon--spin');
                    // Server accepts [lon, lat]
                    var coords = [position.coords.longitude, position.coords.latitude];

                    // Set map view and update indicator position
                    map.setView([coords[1], coords[0]]);
                    circle
                        .setLatLng([coords[1], coords[0]]);

                    // If allow multiple is set (or this is the first time they clicked) add new div
                    if (question.allow_multiple || $(page).find('.question__lon').length === 0) {
                       $(loc_div)
                           .insertBefore(".question__btn");
                    }

                    // Find current length of inputs and update the last one;
                    var questions_lon = $(page).find('.question__lon');
                    var questions_lat = $(page).find('.question__lat');

                    // update array val
                    question.answer[questions_lon.length - 1] = coords;
                        
                    questions_lon[questions_lon.length - 1].value = coords[0];
                    questions_lat[questions_lat.length - 1].value = coords[1];

                }, function error() {
                    //TODO: If cannot Get location" for some reason, 
                    // Allow  user to fill in text field instead
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
    var self = this;
    
    // Map
    var lat = question.answer[0] && question.answer[0][0][1] || App.start_loc[0];
    var lng = question.answer[0] && question.answer[0][0][0] || App.start_loc[1];
    var selected = question.answer[0] && question.answer[0][1] || null;
    App.start_loc = [lat, lng];

    /* Buld inital state */
    var map = L.map('map', {
            center: App.start_loc,
            dragging: true,
            zoom: 13,
            zoomControl: true,
            doubleClickZoom: false,
            attributionControl: false
        });
   
    // Know which marker is currently "up" 
    var touchedMarker = null;
    // Added facility  
    var addedMarker = null;
    // Add markers here so clearing them isn't such a huge pain
    var group = new L.featureGroup();
    group.addTo(map);

    // If selected uuid is stored in the App, paint it green
    if (App.facilities[selected]) {
        addedMarker = addFacility(lat, lng, selected);
        $(page).find('.facility__btn').html("Remove Facility");
    }

    // Revisit API Call calls facilitiesCallback
    getNearbyFacilities(App.start_loc[0], App.start_loc[1], 
            5, // Radius in km 
            question.question_id, // id for localStorage
            facilitiesCallback // what to do with facilities
        );

    // Blinking location indicator
    var circle = L.circle(App.start_loc, 5, {
            color: 'red',
            fillColor: '#f00',
            fillOpacity: 0.5
    })
        .addTo(map);

    var counter = 0;
    function updateColour() {
        var fillcol = Number((counter % 16)).toString(16);
        var col = Number((counter++ % 13)).toString(16);
        circle.setStyle({
            fillColor : "#f" + fillcol + fillcol,
            color : "#f" + col + col,
            zIndexOffset: 777,
        });
    };

    // Save the interval id, clear it every time a page is rendered
    Widgets.interval = window.setInterval(updateColour, 50);

    map.addLayer(App._getMapLayer());

    /* Helper functions for updates  */
    // handles calling drawPoint gets called once per getNearby call 
    function drawFacilities(facilities, clickEvent) {
        group.clearLayers();
        for (i = 0; i < facilities.length; i++) {
            var facility = facilities[i];
            var marker = drawPoint(facility.coordinates[1], 
                        facility.coordinates[0], 
                        facility.name, 
                        facility.properties.sector,
                        facility.uuid,
                        clickEvent);

            // If selected uuid was from Revisit, paint it white
            if (selected == marker.uuid) {
                selectFacility(marker);
            }

            group.addLayer(marker);
        }
    }; 

    function selectFacility(marker) {
        marker.setZIndexOffset(666); // above 250 so it can't be hidden by hovering over neighbour
        marker.setIcon(icon_selected);
        touchedMarker = marker;
        question.answer[0] = [[marker._latlng.lng, marker._latlng.lat], marker.uuid];
        $(page).find('.facility__name').val(marker.name);
        $(page).find('.facility__type').val(marker.sector);
    }

    // callback to handle facilities list, calls drawFacilities
    function facilitiesCallback(facilities) {
        // function that draws facilities and can attach cb on click
        drawFacilities(facilities, function(e) {
            if (addedMarker) {
                App.message("Please remove added facility before choosing an exisiting facility");
                return;
            }

            if (touchedMarker) {
                touchedMarker.setIcon(touchedMarker.type);
                touchedMarker.setZIndexOffset(0);
            }
            
            // Update marker so it looks selected
            var marker = e.target;
            selectFacility(marker);
        });
    }

    // function to wrap up the new facility code
    function addFacility(lat, lng, uuid) {
        var addedMarker = new L.marker([lat, lng], {
            title: "New Facility",
            alt: "New Facility",
            clickable: true,
            draggable: true,
            riseOnHover: true
        });

        addedMarker.uuid = uuid;
        addedMarker.sector = 'other';
        addedMarker.name = "New Facility";
        addedMarker.setIcon(icon_added);
        addedMarker.addTo(map);

        // We added em before 
        if (App.facilities[uuid]) {
            addedMarker.sector = App.facilities[uuid]['properties']['sector'];
            addedMarker.name = App.facilities[uuid]['name'];
        }

        //XXX: Add Popup with bits of info
        addedMarker.on('dragend', function(e) {
            var marker = e.target;
            question.answer[0] = [[marker._latlng.lng, marker._latlng.lat], marker.uuid];
            App.facilities[marker.uuid]['coordinates'] = [marker._latlng.lng, marker._latlng.lat];
        });

        $(page).find('.facility__name').val(addedMarker.name);
        $(page).find('.facility__type').val(addedMarker.sector).change();
        return addedMarker;
    }

    /* Handle events */
    // Widget has two buttons, find location btn (simplifed version of the location widget one)
    // and add facility btn which adds markers onto a map and hooks into revisit
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
                    circle
                        .setLatLng([coords[1], coords[0]])

                    // Revisit api call
                    getNearbyFacilities(coords[1], coords[0],
                            5, // Radius in km 
                            question.question_id, // id for localStorage
                            facilitiesCallback // what to do with facilities
                    );

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


    $(page)
        .find('.facility__btn')
        .click(function() {
            // You added on before
            if (addedMarker) {
                // Get rid of all traces of it
                delete App.facilities[addedMarker.uuid];
                map.removeLayer(addedMarker);
                addedMarker = null;
                question.answer = [];
                this.innerHTML = "Add Facility";
                $(page).find('.facility__name').val("");
                $(page).find('.facility__type').val("other");
                return;
            }

            // Undo selected marker before adding new one
            if (touchedMarker) {
                touchedMarker.setIcon(touchedMarker.type);
                touchedMarker.setZIndexOffset(0);
                touchedMarker = null;
            }

            // Adding new facility
            var lat = map.getCenter().lat;
            var lng = map.getCenter().lng;
            var uuid = GUID(); //XXX: TODO replace this shit with new uuid

            // Get and place marker
            addedMarker = addFacility(lat, lng, uuid);

            // Record this new facility for Revisit submission
            App.facilities[uuid] = {
                'name': 'New Facility', 'uuid': uuid, 
                'properties' : {'sector': 'other'},
                'coordinates' : [lng, lat],
                'question_id' : question.question_id // XXX: Remove this from here
            };

            // Record response for Dokomo
            question.answer[0] = [[lng, lat], uuid];

            this.innerHTML = "Remove Facility";
        });

    // Change name
    $(page)
        .find('.facility__name')
        .keyup(function(e) {
            console.log(this.value);
            if (touchedMarker) {
                // Prevent updates for now
                selectFacility(touchedMarker);
            } else if (addedMarker) {
                // Update facility info
                App.facilities[addedMarker.uuid]['name'] = this.value;
            }
        });

    // Change type
    $(page)
        .find('.facility__type')
        .change(function(e) {
            console.log(this.value);
            if (touchedMarker) {
                // Prevent updates for now
                selectFacility(touchedMarker);
            } else if (addedMarker) {
                // Update facility info
                App.facilities[addedMarker.uuid]['properties']['sector'] = this.value;
            } 
        });
};

// Handle creating multiple inputs for widgets that support it 
Widgets._addNewInput = function(page, question, cls, type, keyup_cb, change_cb) {
    if (question.allow_multiple) {
        $('<input>')
            .attr({'type': type, 'class': cls})
            .change(change_cb)
            .keyup(keyup_cb)
            .insertBefore(page.find(".next_input"))
            .focus();
    }
}

/* -------------------------- Revisit Stuff Below ----------------------------*/
function getNearbyFacilities(lat, lng, rad, id, cb) {
    var url = "http://staging.revisit.global/api/v0/facilities.json" 
    //var url = "http://localhost:3000/api/v0/facilities.json" // install revisit server from git
    if (navigator.onLine) { //TODO: Do query only when necessary somehow 
        // Revisit ajax req
        console.log("MADE EXTERNAL QUERY");
        $.get(url,{
                near: lat + "," + lng,
                rad: rad,
                limit: 256,
                fields: "name,uuid,coordinates,properties:sector", //filters results to include just those three fields,
            },
            function(data) {
                localStorage.setItem(id, JSON.stringify(data));
                if (cb) {
                    cb(data.facilities);
                }
            }
        );

    } else {
        console.log("MADE LOCAL QUERY");
        var revisit = localStorage.getItem(id);
        var facilities = revisit && JSON.parse(revisit).facilities || [];
        cb(facilities);
    }
}

function postNewFacility(facility) {
    var url = "http://staging.revisit.global/api/v0/facilities.json";
    //var url = "http://localhost:3000/api/v0/facilities.json" // install revisit server from git

    // For local storage referencing
    var id = facility.question_id;
    delete facility.question_id; //XXX; Pass in question id instead

    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(facility),
        dataType: 'json',
        success: function() {
            App.message('Facility Added!');

            // Javascript single-threadedness makes this safe. Async doesn't switch tasks mid execution
            var revisit = localStorage.getItem(id);
            var facilities = revisit && JSON.parse(revisit).facilities || [];
            facilities.push(facility);
            localStorage.setItem(id, JSON.stringify({"facilities": facilities})); // store in localstorage incase they lose connection even after posting

            // If posted, we don't an unsynced reference to it anymore
            delete App.facilities[facility.uuid];
            //localStorage['facilities'] = App.facilities;
        },
        fail: function() {
            App.message('Facility submission failed, will try again later.');
            //XXX: Do something here so that users can create additional facilities even one is unposted 
        },
        error: function() {
            App.message('Facility submission failed, will try again later.');
            //XXX: Do something here so that users can create additional facilities even one is unposted 
        }
    });
}

var icon_edu = new L.icon({iconUrl: "/static/img/icons/normal_education.png",iconAnchor: [13, 31]});
var icon_health = new L.icon({iconUrl: "/static/img/icons/normal_health.png", iconAnchor: [13, 31]});
var icon_water = new L.icon({iconUrl: "/static/img/icons/normal_water.png", iconAnchor: [13, 31]});
var icon_selected = new L.icon({iconUrl: "/static/img/icons/selected-point.png", iconAnchor: [15, 48]});
var icon_added = new L.icon({iconUrl: "/static/img/icons/added-point.png", iconAnchor: [15, 48]});

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

    switch(type) {
        case "education":
            marker.options.icon = icon_edu;
            marker.type = icon_edu;
            break;
        case "water":
            marker.options.icon = icon_water;
            marker.type = icon_water;
            break;
        case "health":
            marker.options.icon = icon_health; 
            marker.type = icon_health;
            break;
        default:
            // just mark it as health 
            marker.options.icon = icon_health; 
            marker.type = icon_health;
            marker.sector = 'other';
            //XXX: Mark health as health and create default icon
            break;
    }

    marker.on('click', clickEvent);
    return marker;
    
};

// Not sure how legit this is but hey
function GUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}
