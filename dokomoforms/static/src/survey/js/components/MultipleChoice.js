var React = require('react'),
    createReactClass = require('create-react-class');
var Select = require('./baseComponents/Select.js');

/*
 * Multiple choice question component
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
        return {
        }
    },

    /*
     * Hack to force react to update child components
     * Gets called by parent element through 'refs' when state of something changed
     * (usually localStorage)
     */
    update: function() {
    },

    /*
     * Record all selected options into localStorage
     */
    onSelect: function(values) {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        answers = [];
        values.forEach(function(value, index) {
            if (value == 'null')
                return;
            answers.push({
                'response': value === 'other' ? '' : value,
                'response_type': value === 'other' ? 'other' : 'answer'
            });
        });

        console.log("values", values, answers)
        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

    },

    /*
     * Record other response into existing slot of answer object in localStorage
     * Callback is only called on validated input
     */
    onInput: function(value) {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        answers.forEach(function(answer, index) {
            if (answer.response_type === 'other') {
                answer.response = value;
                return false;
            }
            return true;
        });

        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

    },

    /*
     * Get all selected options from localStorage
     */
    getSelection: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        var values = [];
        answers.forEach(function(answer, index) {
            values[index] = answer.response;
            if (answer.response_type === 'other')
                values[index] = 'other';
        });

        console.log("values", values)
        return values;
    },

    /*
     * Get other response if any from localStorage
     */
    getAnswer: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        var response = null;
        answers.forEach(function(answer, index) {
            if (answer.response_type === 'other') {
                response = answer.response;
                return false;
            }

            return true;
        });

        console.log("response", response);
        return response;
    },

    render: function() {
        var self = this;
        var choices = this.props.question.choices.map(function(choice) {
            return {
                'value': choice.choice_id,
                'text': choice.choice_text[self.props.language]
            }
        });

        // Key is used as hack to rerender select on dontKnow state change
        return (<Select
                    key={this.props.disabled}
                    choices={choices}
                    withOther={this.props.question.allow_other}
                    multiSelect={this.props.question.allow_multiple}
                    disabled={this.props.disabled}
                    initValue={this.getAnswer()}
                    initSelect={this.getSelection()}
                    onSelect={this.onSelect}
                    onInput={this.onInput}
                />)
    }
});
