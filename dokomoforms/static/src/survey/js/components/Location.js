var React = require('react'),
    createReactClass = require('create-react-class'),
    ResponseField = require('./baseComponents/ResponseField.js'),
    LittleButton = require('./baseComponents/LittleButton.js'),

    locationService = require('../services/location');

/*
 * Location question component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 *     @disabled: boolean for disabling all inputs
 */
module.exports = createReactClass({
    getInitialState: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;

        return {
            questionCount: length
        };
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
            questionCount: length
        });
    },

    /*
     * Add new input if and only if they've responded to all previous inputs
     */
    addNewInput: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length;

        console.log('Length:', length, 'Count', this.state.questionCount);
        if (answers[length] && answers[length].response_type || length > 0 && length == this.state.questionCount) {

            this.setState({
                questionCount: this.state.questionCount + 1
            });
        }
    },

    /*
     * Remove input and update localStorage
     */
    removeInput: function(index) {
        console.log('Remove', index);

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        answers.splice(index, 1);
        survey[this.props.question.id] = answers;

        localStorage[this.props.surveyID] = JSON.stringify(survey);


        var count = this.state.questionCount;
        if (this.state.questionCount > 1)
            count = count - 1;

        this.setState({
            questionCount: count
        });

        this.forceUpdate();
    },

    /*
     * Retrieve location and record into localStorage on success.
     * Updates questionCount on success, triggering rerender of page
     * causing input fields to have values reloaded.
     *
     * Only updates the LAST active input field.
     */
    onLocate: function() {
        var self = this;
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var index = answers.length === 0 ? 0 : this.refs[answers.length] ? answers.length : answers.length - 1; // So sorry
        // var position = locationService.getCurrentPosition();

        function positionFound(position) {
            var loc = {
                'lat': position.coords.latitude,
                'lng': position.coords.longitude
            };

            // Record location for survey
            localStorage['location'] = JSON.stringify(loc);

            answers[index] = {
                'response': loc,
                'response_type': 'answer'
            };

            survey[self.props.question.id] = answers; // Update localstorage
            localStorage[self.props.surveyID] = JSON.stringify(survey);

            var length = answers.length === 0 ? 1 : answers.length;
            self.setState({
                questionCount: length
            });
        }

        locationService.fetchPosition(positionFound);
        // if (position) {
        //     positionFound(position);
        // } else {
        // }

        // navigator.geolocation.getCurrentPosition(
        //     function success(position) {
        //         var loc = {
        //             'lat': position.coords.latitude,
        //             'lng': position.coords.longitude
        //         };

        //         // Record location for survey
        //         localStorage['location'] = JSON.stringify(loc);

        //         answers[index] = {
        //             'response': loc,
        //             'response_type': 'answer'
        //         };

        //         survey[self.props.question.id] = answers; // Update localstorage
        //         localStorage[self.props.surveyID] = JSON.stringify(survey);

        //         var length = answers.length === 0 ? 1 : answers.length;
        //         self.setState({
        //             questionCount: length
        //         });
        //     },

        //     function error() {
        //         console.log('Location could not be grabbed');
        //     },

        //     {
        //         enableHighAccuracy: true,
        //         timeout: 20000,
        //         maximumAge: 0
        //     }
        // );


    },

    /*
     * Get default value for an input at a given index from localStorage
     *
     * @index: The location in the answer array in localStorage to search
     */
    getAnswer: function(index) {
        console.log('In:', index);

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        console.log(answers, index);
        var response = answers[index] && answers[index].response || null;
        return response ? response.lat + ', ' + response.lng : null;
    },

    render: function() {
        var children = Array.apply(null, {
            length: this.state.questionCount
        });
        var self = this;
        return (
            <span>
                <LittleButton
                    buttonFunction={this.onLocate}
                    iconClass={'icon-star'}
                    text={'find my location'}
                />
                {children.map(function(child, idx) {
                    return (
                            <ResponseField
                                buttonFunction={self.removeInput}
                                type={self.props.questionType}
                                key={Math.random()}
                                index={idx}
                                ref={idx}
                                disabled={true}
                                initValue={self.getAnswer(idx)}
                                showMinus={true}
                            />
                           );
                })}
                {this.props.question.allow_multiple
                    ? <LittleButton buttonFunction={this.addNewInput}
                        disabled={this.props.disabled}
                        text={'add another answer'} />
                    : null
                }
            </span>
        );
    }
});
