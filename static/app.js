App = {
    unsynced: [] // unsynced surveys
};

App.init = function(survey) {
    var self = this;
    self.survey = new Survey(survey.survey_id, survey.questions);

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


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function Survey(id, questions) {
    var self = this;
    this.id = id;
    this.questions = questions;
    //this.questions = _.sortBy(questions, function(question) { return question.sequence_number; });

    // Load answers from localStorage
    var answers = JSON.parse(localStorage[this.id] || '{}');
    _.each(this.questions, function(question) {
        question.answer = answers[question.question_id] || [];
    });
    
    // Page navigation
    $('.page_nav__prev, .page_nav__next').click(function() {
        var offset = this.classList.contains('page_nav__prev') ? -1 : 1;
        var index = $('.content').data('index') + offset;
        if (index >= 0 && index <= self.questions.length) {
            self.next(offset, index);
        }
        return false;
    });
    
    // Render first question
    this.render(0);
};

Survey.prototype.next = function(offset, index) {
    var self = this;
    var prev_index = index - offset;
    var prev_question = this.questions[prev_index];
    if (offset === 1 && prev_question) {
        // XXX: prev_question.answer field is a mess to check, need to purify ans
        if (prev_question.logic.required 
                && (!prev_question.answer[0] && prev_question.answer !== 0))  {
            App.message('Survey requires this question to be completed.');
            return;
        }
    }

    self.render(index);
};

//XXX: Have a question class to do checks, answer validation and branching? 

Survey.prototype.render = function(index) {
    var self = this;
    var question = this.questions[index];
    var content = $('.content');
    
    if (question) {
        // Show widget
        var templateHTML = $('#widget_' + question.type_constraint_name).html();
        var template = _.template(templateHTML);
        var html = template({question: question});
        
        // Render question
        content.empty()
            .data('index', index)
            .html(html)
            .scrollTop(); //XXX: Ignored in chrome ...
        
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
        .text((index + 1) + ' / ' + (this.questions.length + 1));
};

Survey.prototype.submit = function() {
    var self = this;
    var sync = $('.nav__sync')[0];
    var save_btn = $('.question__saving')[0];
    var answers = {};
    
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

            if (!ans) 
                return;

            answers.push({
                question_id: q.question_id,
                answer: ans,
                is_other: is_other_val 
            });
        });
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
      }, 1000);
      return;
    }

    // TODO: Deal with 500 in firefox
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
        }
    }).done(function() {
        setTimeout(function() {
            sync.classList.remove('icon--spin');
            save_btn.classList.remove('icon--spin');
            self.render(0);
        }, 1000);
    });
};


var Widgets = {};

// Handle creating multiple inputs for widgets that support it (might not be best place to store func)
Widgets.keyUp = function(e, page, question, cls, type, keyup_cb, change_cb) {
    //TODO: Instead of enter key, listen to btn press to display new box 
    if (e.keyCode === 13) {
        if (question.allow_multiple) {
            $('<input>')
                .attr({'type': type, 'class': cls})
                .change(change_cb)
                .keyup(keyup_cb)
                .appendTo(page)
                .focus();
        }
    }
}

// All widgets store results in the questions.answer array
Widgets.text = function(question, page) {
    // This widget's events. Called after page template rendering.
    // Responsible for setting the question object's answer
    //
    // question: question data
    // page: the widget container DOM element

    var self = this;
    function keyup(e) {
        var ans_ind = ($(page).find('input')).index(this);
        question.answer[ans_ind] = this.value;
        self.keyUp(e, page, question, 'text_input', 'text', keyup);
    };

    $(page)
        .find('input')
        .keyup(keyup);
};

Widgets.integer = function(question, page) {
    var self = this;
    function keyup(e) {
        var ans_ind = ($(page).find('input')).index(this);
        question.answer[ans_ind] = parseInt(this.value);
        self.keyUp(e, page, question, 'text_input', 'number', keyup);
    };

    $(page)
        .find('input')
        .keyup(keyup);
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

Widgets.decimal = function(question, page) {
    var self = this;
    function keyup(e) {
        var ans_ind = ($(page).find('input')).index(this);
        question.answer[ans_ind] = parseFloat(this.value);
        self.keyUp(e, page, question, 'text_input', 'number', keyup);
    };

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
        self.keyUp(e, page, question, 'text_input', 'date', keyup, change);
    }

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
        self.keyUp(e, page, question, 'text_input', 'time', keyup, change);
    }

    $(page)
        .find('input')
        .change(change)
        .keyup(keyup)
};

Widgets.note = function(question, page) {
};

Widgets.location = function(question, page) {
    // TODO: add location status
    var self = this;
    
    // Map
    var lat = parseFloat($(page).find('.question__lat').val()) || 5.118915;
    var lng = parseFloat($(page).find('.question__lon').val()) || 7.353078;
    var start_loc = [lat, lng];

    var map = L.map('map', {
            center: start_loc,
            dragging: true,
            zoom: 16,
            zoomControl: false,
            doubleClickZoom: false,
            attributionControl: false
        });
    
    // Revisit API Call
    getNearbyFacilities(start_loc[0], start_loc[1], 2, map); 

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
    var funcLayer = new L.TileLayer.Functional(function(view) {
        var deferred = $.Deferred();
        var url = 'http://{s}.tiles.mapbox.com/v3/examples.map-20v6611k/{z}/{y}/{x}.png'
            .replace('{s}', 'abcd'[Math.round(Math.random() * 3)])
            .replace('{z}', Math.floor(view.zoom))
            .replace('{x}', view.tile.row)
            .replace('{y}', view.tile.column);
        getImage(url, deferred.resolve);
        return deferred.promise();
    });
    
    map.addLayer(funcLayer);

    // Location is the only one that doesn't use the same keyup function due to the btn
    // being the only way to input values in the view.
    var loc_div = "<div class='loc_input'><input class='text_input question__lat' type='text'><input class='text_input question__lon' type='text'></div>";

    $(page)
        .find('.question__btn')
        .click(function() {
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var coords = [position.coords.longitude, position.coords.latitude];

                    map.setView([coords[1], coords[0]]);

                    // Revisit api call
                    getNearbyFacilities(coords[0], coords[1], 2, map); 

                    var questions_lon = $(page).find('.question__lon');
                    var questions_lat = $(page).find('.question__lat');

                    questions_lon[questions_lon.length - 1].value = coords[0];
                    questions_lat[questions_lat.length - 1].value = coords[1];
                    // update array val
                    question.answer[questions_lon.length - 1] = coords;

                    // Add new button if allow multiple is present 
                    if (question.allow_multiple) {
                       var loc_dom = $(loc_div)
                            .find('input')

                       $('.question__btn').before(loc_dom);
                    }

                }, function error() {
                    alert('error')
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });
};


/* Revisit stuff */
function getNearbyFacilities(lat, lng, rad, map) {
    var icon_edu = new L.icon({iconUrl: "/static/img/icons/normal_education.png"});
    var icon_health = new L.icon({iconUrl: "/static/img/icons/normal_health.png"});
    var icon_water = new L.icon({iconUrl: "/static/img/icons/normal_water.png"});
    var url = "http://revisit.global/api/v0/facilities.json"
    function drawPoint(lat, lng, name, type) {
        var marker = new L.marker([lat, lng], {
            title: name,
            alt: name,
            riseOnHover: true
        });

        switch(type) {
            case "education":
                marker.options.icon = icon_edu;
                break;
            case "water":
                marker.options.icon = icon_water;
                break;
            default:
                // just mark it as health 
                marker.options.icon = icon_health;
                break;
        }

        marker.addTo(map);
    };

    var revisit = localStorage.getItem('revisit');
    if (revisit) { // its in localStorage 
        var facilities = JSON.parse(revisit).facilities;
        var facility = null;
        for(i = 0; i < facilities.length; i++) {
            facility = facilities[i];
            // stored lon/lat in revisit, switch around
            drawPoint(facility.coordinates[1], 
                    facility.coordinates[0], 
                    facility.name, 
                    facility.properties.sector);
        }
    } else {
        // Revisit ajax req
        $.get(url,{
                near: lat + "," + lng,
                rad: rad,
                limit: 100,
                fields: "name,coordinates,properties:sector", //filters results to include just those three fields,
            },
            function(data) {
                localStorage.setItem('revisit', JSON.stringify(data));
                var facilities = data.facilities;
                var facility = null;
                for(i = 0; i < facilities.length; i++) {
                    facility = facilities[i];
                    // stored lon/lat in revisit, switch around
                    drawPoint(facility.coordinates[1], 
                            facility.coordinates[0], 
                            facility.name, 
                            facility.properties.sector);
                }
            }
        );
    }
}
