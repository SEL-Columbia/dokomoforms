var React = require('react');

var ResponseField = require('./baseComponents/ResponseField.js');
var ResponseFields = require('./baseComponents/ResponseFields.js');
var LittleButton = require('./baseComponents/LittleButton.js');

var FacilityRadios = require('./baseComponents/FacilityRadios.js');
var Select = require('./baseComponents/Select.js');

module.exports = React.createClass({
    getInitialState: function() {
        return { 
            facilities: [],
            addFacility: true,
        }
    },

    addNewInput: function() {
        this.setState({
            questionCount: this.state.questionCount + 1
        })
    },

    removeInput: function() {
        if (!(this.state.questionCount > 1))
            return;

        this.setState({
            questionCount: this.state.questionCount - 1
        })
    },

    toggleAddFacility: function() {
        this.setState({
            addFacility : this.state.addFacility ? false : true
        })
    },

    getFacilities: function() {
    },

    render: function() {
        var choices = [
            {'text': {'English': 'Water'}, 'value': 'water'},
            {'text': {'English': 'Energy'}, 'value': 'energy'},
            {'text': {'English': 'Education'}, 'value': 'education'},
        ];

        return (
                <span>
                 <LittleButton buttonFunction={this.getFacilities}
                    icon={'icon-star'}
                    text={'find my location and show nearby facilities'} />
                {this.state.addFacility ?
                    <span>
                    <FacilityRadios facilities={this.state.facilities}/>
                        <LittleButton buttonFunction={this.toggleAddFacility}
                            text={'add another answer'} />
                    </span>
                :
                    <span>
                    <ResponseField type={'text'}/>
                    <ResponseField type={'location'}/>
                    <Select choices={choices} withOther={true} multiSelect={false}/>
                        <LittleButton buttonFunction={this.toggleAddFacility}
                            text={'cancel'} />
                    </span>
                }
                </span>
               )
    }
});
