var React = require('react'),
    createReactClass = require('create-react-class');

var ResponseField = require('./baseComponents/ResponseField.js');
var LittleButton = require('./baseComponents/LittleButton.js');

/*
 * Question component
 * The default question controller-view
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
        if (answers[length] && answers[length].response_type || length > 0 && length === this.state.questionCount) {

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

        if (!(this.state.questionCount > 1))
            return;

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        answers.splice(index, 1);
        survey[this.props.question.id] = answers;

        localStorage[this.props.surveyID] = JSON.stringify(survey);

        this.setState({
            questionCount: this.state.questionCount - 1
        });

        //this.forceUpdate();
    },

    /*
     * Record new response into localStorage, response has been validated
     * if this callback is fired
     */
    onInput: function(value, index) {

        console.log('Hey', index, value);
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];

        //XXX Null value implies failed validation
        answers[index] = {
            'response': value,
            'response_type': 'answer'
        };

        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

        //if (value === null) {
        //    this.removeInput(index);
        //}
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
        return answers[index] && answers[index].response || null;
    },

    render: function() {
        var children = Array.apply(null, {
            length: this.state.questionCount
        });
        var self = this;
        return (
            <span>
                {children.map(function(child, idx) {
                    return (
                            <ResponseField
                                buttonFunction={self.removeInput}
                                onInput={self.onInput}
                                type={self.props.questionType}
                                logic={self.props.question.logic}
                                key={Math.random()}
                                index={idx}
                                disabled={self.props.disabled}
                                initValue={self.getAnswer(idx)}
                                showMinus={self.state.questionCount > 1}
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
