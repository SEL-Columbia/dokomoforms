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
    console.log(prev_question.answers, prev_question);
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
            .html(html);
        
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
        q.answer.forEach(function(ans) {
            answers.push({
                question_id: q.question_id,
                answer: ans,
                is_other: q.is_other || false //XXX: This will need to be an array as well
            });
        });
    });

    var data = {
        survey_id: self.id,
        answers: answers
    };

    console.log(data);
    
    sync.classList.add('icon--spin');
    save_btn.classList.add('icon--spin');

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
            App.message('Survey submitted!');
            self.render(0);
        }, 1000);
    });
};


var Widgets = {};

// Handle creating multiple inputs for widgets that support it
Widgets.keyUp = function(e, page, question, cls, type, keyup_cb) {
    if (e.keyCode === 13) {
        if (question.allow_multiple) {
            var v = $('<input>')
                .attr({'type': type, 'class': cls})
                .keyup(keyup_cb)
                .appendTo(page);
        }
    }
}

Widgets.text = function(question, page) {
    // This widget's events. Called after page template rendering.
    // Responsible for setting the question object's answer
    //
    // question: question data
    // page: the widget container DOM element
    $(page)
        .find('input')
        .on('keyup', function() {
            question.answer = [this.value];
        });
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

Widgets.location = function(question, page) {
    // TODO: add location status
    
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

    $(page)
        .find('.question__btn')
        .click(function() {
            navigator.geolocation.getCurrentPosition(
                function success(position) {
                    // Server accepts [lon, lat]
                    var coords = [position.coords.longitude, position.coords.latitude];
                    question.answer = [coords];

                    map.setView([coords[1], coords[0]]);

                    // Revisit api call
                    getNearbyFacilities(coords[0], coords[1], 2, map); 

                    $(page).find('.question__lon').val(coords[0]);
                    $(page).find('.question__lat').val(coords[1]);
                }, function error() {
                    alert('error')
                }, {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                });
        });
};

Widgets.multiple_choice = function(question, page) {
    var $other = $(page)
        .find('.text_input')
        .keyup(function() {
            question.answer = [this.value];
        })

    $other.hide();

    var $select = $(page)
        .find('select')
        .change(function() {
            if (this.value == 'null') {
                // No option chosen
                question.answer = [];
                question.is_other = false;
                $other.hide();
            } else if (this.value == 'other') {
                // Choice is text input
                $other.show();
                question.answer = [$other.val()];
                question.is_other = true;
            } else {
                // Normal choice
                question.answer = [this.value];
                question.is_other = false;
                $other.hide();
            }
        });

    if (question.is_other) {
        $select.find("#with_other").prop("selected", true);
        $other.show();
    }

};

Widgets.decimal = function(question, page) {
    $(page)
        .find('input')
        .keyup(function() {
            question.answer = [parseFloat(this.value)];
        });
};

Widgets.date = function(question, page) {
    $(page)
        .find('input')
        .change(function() {
            if (this.value !== '') {
                question.answer = [this.value];
            }
        });
};

Widgets.time = function(question, page) {
    $(page)
        .find('input')
        .change(function() {
            if(this.value !== ''){
                question.answer = [this.value];
            }
      });
};

Widgets.note = function(question, page) {
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
