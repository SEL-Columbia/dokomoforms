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
        return { 
            loc: null,
            addFacility: true,
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
            addFacility : this.state.addFacility ? false : true
        })
    },

    getFacilities: function() {
        if (!this.state.loc)
          return [];  

        console.log("Getting facilities ...");
        return this.props.tree.getNNearestFacilities(this.state.loc.lat, this.state.loc.lng, 1000, 10);
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

                self.setState({
                    loc: loc 
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
                {this.state.addFacility ?
                    <span>
                    <FacilityRadios facilities={this.getFacilities()}/>
                    <LittleButton buttonFunction={this.toggleAddFacility}
                            text={'add another answer'} />
                    </span>
                :
                    <span>
                    <ResponseField type={'text'}/>
                    <ResponseField type={'location'}/>
                    <Select 
                        choices={choices} 
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
