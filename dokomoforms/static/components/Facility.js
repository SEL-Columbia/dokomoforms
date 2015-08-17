var React = require('react');
var Promise = require('mpromise');

var ResponseField = require('./baseComponents/ResponseField.js');
var ResponseFields = require('./baseComponents/ResponseFields.js');
var LittleButton = require('./baseComponents/LittleButton.js');

var FacilityRadios = require('./baseComponents/FacilityRadios.js');
var Select = require('./baseComponents/Select.js');

/*
 * Facilities question component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 *     @disabled: boolean for disabling all inputs
 *     @db: pouchdb database 
 *     @tree: Facility Tree object
 */
module.exports = React.createClass({
    getInitialState: function() {
        var self = this;
        var answer = this.getAnswer();
        var selectOff = answer && answer.metadata && answer.metadata.is_new;
        return { 
            loc: null,
            selectFacility: !selectOff,
            facilities: [],
            choices: [
                {'value': 'water', 'text': 'Water'}, 
                {'value': 'energy', 'text': 'Energy'}, 
                {'value': 'education', 'text': 'Education'}, 
                {'value': 'health', 'text': 'Health'}, 
            ],
        }
    },

    /* 
     * Deal with async call to getFacilities
     */
    componentWillMount: function() {
        var loc = JSON.parse(localStorage['location'] || '{}');
        var self = this;
        self.getFacilities(loc).onResolve(function(err, facilities) {
            self.setState({
                loc: loc,
                facilities: facilities
            });
        });
    },
    /*
     * Hack to force react to update child components
     * Gets called by parent element through 'refs' when state of something changed 
     * (usually localStorage)
     */
    update: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;
        this.setState({
            questionCount: length,
        });
    },

    /*
     * Switch view to new Facility View
     */
    toggleAddFacility: function() {
        this.setState({
            selectFacility : this.state.selectFacility ? false : true
        })
    },

    /*
     * Record newly chosen facility into localStorage
     *
     * @option: The facility uuid chosen
     * @data: I have no idea why i have this?
     */
    selectFacility: function(option, data) {
        console.log("Selected facility");
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        answers = [];

        this.state.facilities.forEach(function(facility) {
            if (facility.uuid === option) {
                answers = [{
                    'response': {
                        'facility_id': facility.uuid,
                        'facility_name': facility.name,
                        'facility_sector': facility.properties.sector,
                        'lat': facility.coordinates[1],
                        'lng': facility.coordinates[0],
                    }, 
                    'response_type': 'answer'
                }];
                return false;
            }
            return true;
        });

        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);
        
    },

    /* 
     * Query the tree for nearby facilities near given location when possible
     *
     * @loc: The location ({lat: NUM, lng: NUM}) to query around
     */
    getFacilities: function(loc) {
        if (!loc || !loc.lat || !loc.lng || !this.props.tree || !this.props.tree.root) {
            var p = new Promise;
            p.fulfill([]);
            return p;
        }

        console.log("Getting facilities ...");
        return this.props.tree.getNNearestFacilities(loc.lat, loc.lng, 1000, 10);
    },

    /*
     * Get response from localStorage
     */ 
    getAnswer: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        console.log("Selected facility", answers[0]);
        if (answers[0]) 
            return answers[0]
    },

    /*
     * Generate objectID compatitable with Mongo for the Revisit API
     *
     * Returns an objectID string
     */
    createObjectID: function() {
       return 'xxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[x]/g, function() {
           var r = Math.random()*16|0;
           return r.toString(16);
       });
    },

    /*
     * Deal with all new facility input fields, type is bound to function call
     *
     * @type: Type of input that was updated
     * @value: newly supplied input
     */
    onInput: function(type, value) {
        console.log("Dealing with input", value, type);
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var self = this;
        if (answers[0] && (!answers[0].metadata || !answers[0].metadata.is_new)) {
            answers = [];
        }

        // Load up previous response, update values
        var response = (answers[0] && answers[0].response) || {}; 
        var uuid = response.facility_id || this.createObjectID();
        response.facility_id = uuid;
        // XXX This kind of assumes that current lat/lng is correct at the time of last field update
        response.lat = this.state.loc.lat; 
        response.lng = this.state.loc.lng; 

        switch(type) {
            case 'text':
                response.facility_name = value;
                break;
            case 'select':
                var v = value[0]; // Only one ever
                console.log('Selected v', v);
                response.facility_sector = v;
                break;
            case 'other':
                console.log('Other v', value);
                response.facility_sector = value;
                break;
        }

        //XXX Failed validation messes up facility question
        //TODO: Properly handle null values
       
        answers = [{
            'response': response,
            'response_type': 'answer',
            'metadata': {
                'is_new': true
            }
        }];

        console.log("Built response", answers);

        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);
    },


    /*
     * Retrieve location and record into state on success.
     */
    onLocate: function() {
        var self = this;
        navigator.geolocation.getCurrentPosition(
            function success(position) {
                var loc = {
                    'lat': position.coords.latitude,
                    'lng': position.coords.longitude, 
                }

                // Record location for survey
                localStorage['location'] = JSON.stringify(loc);

                self.getFacilities(loc).onResolve(function(err, facilities) {
                    self.setState({
                        loc: loc,
                        facilities: facilities
                    });
                });
            }, 
            
            function error() {
                console.log("Location could not be grabbed");
            }, 
            
            {
                enableHighAccuracy: true,
                timeout: 20000,
                maximumAge: 0
            }
        );


    },

    render: function() {
        // Retrieve respone for initValues
        var answer = this.getAnswer();
        var choiceOptions = this.state.choices.map(function(choice) { return choice.value });

        var hasLocation = this.state.loc && this.state.loc.lat && this.state.loc.lng;
        var isNew = answer && answer.metadata && answer.metadata.is_new;

        // Update sector field to match initSelect expected value
        var sector = answer && answer.response.facility_sector;
        var isOther = choiceOptions.indexOf(sector) === -1;
        sector = isOther ? sector && 'other' : sector; 

        return (
                <span>
                {this.state.selectFacility ?
                    <span>
                    <LittleButton buttonFunction={this.onLocate}
                        icon={'icon-star'}
                        text={'find my location and show nearby facilities'} 
                        disabled={this.props.disabled}
                    />

                    <FacilityRadios 
                        key={this.props.disabled}
                        selectFunction={this.selectFacility} 
                        facilities={this.state.facilities}
                        initValue={answer && !isNew && answer.response.facility_id}
                        disabled={this.props.disabled}
                    />

                    { hasLocation  ?
                        <LittleButton buttonFunction={this.toggleAddFacility}
                            disabled={this.props.disabled}
                            text={'add new facility'} 
                        />
                        : null
                    }
                    </span>
                :
                    <span>
                    <ResponseField 
                        onInput={this.onInput.bind(null, 'text')}
                        initValue={isNew && answer.response.facility_name}
                        type={'text'}
                        disabled={this.props.disabled}
                    />
                    <ResponseField 
                        initValue={JSON.stringify(this.state.loc)} 
                        type={'location'}
                        disabled={true}
                    />
                    <Select 
                        choices={this.state.choices} 
                        initValue={isNew && isOther ? answer.response.facility_sector : null}
                        initSelect={isNew && [sector]} 
                        withOther={true} 
                        multiSelect={false}
                        onInput={this.onInput.bind(null, 'other')}
                        onSelect={this.onInput.bind(null, 'select')}
                        disabled={this.props.disabled}
                    />

                    <LittleButton 
                        buttonFunction={this.toggleAddFacility} 
                            text={'cancel'} 
                            disabled={this.props.disabled}
                     />

                    </span>
                }
                </span>
               )
    }
});
