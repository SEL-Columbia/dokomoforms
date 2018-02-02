var React = require('react'),
    createReactClass = require('create-react-class');
var BigButton = require('./baseComponents/BigButton.js');
var DontKnow = require('./baseComponents/DontKnow.js');
var ResponseField = require('./baseComponents/ResponseField.js');

/*
 * Footer component
 * Render footer containing a button and possible DontKnow component
 *
 * props:
 *  @showDontKnow: Boolean to activate DontKnow component
 *  @checkBoxFunction: What do on DontKnow component click event
 *  @buttonText: Text to show on big button
 *  @buttonType: Type of big button to render
 *  @showDontKnowBox: Boolean to extend footer and show input field
 *  @questionID: id of active question (if any)
 *  @surveyID: id of active survey
 */
module.exports = createReactClass({
    getDontKnow: function() {
        if (this.props.showDontKnow)
            return (
                <DontKnow
                    checkBoxFunction={this.onCheck}
                    key={this.props.questionID}
                    checked={this.props.showDontKnowBox}
                />
            );

        return null;
    },

    /*
     * Record new response into localStorage, response has been validated
     * if this callback is fired
     */
    onInput: function(value, index) {

        console.log('Hey', index, value);
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');

        var answers = [{
            'response': value,
            'response_type': 'dont_know'
        }];

        survey[this.props.questionID] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

    },

    /*
     * Clear localStorage when dont know is checked
     * Call checkBoxFunction if supplied
     *
     * @event: click event on checkbox
     */
    onCheck: function(event) {
        // Clear responses
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        survey[this.props.questionID] = [];
        localStorage[this.props.surveyID] = JSON.stringify(survey);

        if (this.props.checkBoxFunction) {
            this.props.checkBoxFunction(event);
        }
    },

    /*
     * Get default value for an input at a given index from localStorage
     */
    getAnswer: function(questionID) {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[questionID] || [];
        return answers[0] && answers[0].response_type === 'dont_know' && answers[0].response || null;
    },


    render: function() {
        var FooterClasses = 'bar bar-standard bar-footer';
        if (this.props.showDontKnow)
            FooterClasses += ' bar-footer-extended';
        if (this.props.showDontKnowBox)
            FooterClasses += ' bar-footer-extended bar-footer-super-extended';

        var self = this;
        return (
            <div className={FooterClasses}>
                <BigButton text={this.props.buttonText}
                type={this.props.buttonType}
                buttonFunction={this.props.buttonFunction} />
                { this.getDontKnow() }
                { this.props.showDontKnowBox ?
                    <ResponseField
                            placeholder='Please explain...'
                            index={0}
                            onInput={self.onInput}
                            initValue={self.getAnswer(self.props.questionID)}
                            type={'text'}
                    />
                : null}
            </div>
        );
    }
});
