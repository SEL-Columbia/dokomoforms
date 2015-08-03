var React = require('react');

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
        var loc = null;
        return { 
            loc: loc,
            selectFacility: true,
            facilities: self.getFacilities(loc),
            choices: [
                {'value': 'water', 'text': 'Water'}, 
                {'value': 'energy', 'text': 'Energy'}, 
                {'value': 'education', 'text': 'Education'}, 
                {'value': 'health', 'text': 'Health'}, 
            ],
        }
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

    toggleAddFacility: function() {
        this.setState({
            selectFacility : this.state.selectFacility ? false : true
        })
    },

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

    getFacilities: function(loc) {
        if (!loc)
          return [];  

        console.log("Getting facilities ...");
        return this.props.tree.getNNearestFacilities(loc.lat, loc.lng, 1000, 10);
    },

    getAnswer: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        console.log("Selected facility", answers[0]);
        return answers[0] && answers[0].response;
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

                var facilities = self.getFacilities(loc);
                self.setState({
                    loc: loc,
                    facilities: facilities
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
        return (
                <span>
                 <LittleButton buttonFunction={this.onLocate}
                    icon={'icon-star'}
                    text={'find my location and show nearby facilities'} />
                {this.state.selectFacility ?
                    <span>
                    <FacilityRadios 
                        selectFunction={this.selectFacility} 
                        facilities={this.state.facilities}
                        initValue={this.getAnswer()}
                    />
                    <LittleButton buttonFunction={this.toggleAddFacility}
                            text={'add new facility'} />
                    </span>
                :
                    <span>
                    <ResponseField type={'text'}/>
                    <ResponseField type={'location'}/>
                    <Select 
                        choices={this.state.choices} 
                        withOther={true} 
                        multiSelect={false}
                    />

                    <LittleButton 
                        buttonFunction={this.toggleAddFacility} 
                            text={'cancel'} 
                     />

                    </span>
                }
                </span>
               )
    }
});
