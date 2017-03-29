import React from 'react';
import BigButton from './baseComponents/BigButton.js';
import DontKnow from './baseComponents/DontKnow.js';
import ResponseField from './baseComponents/ResponseField.js';

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
export default class Footer extends React.Component {

    constructor(props) {
        super(props);

        this.getDontKnow = this.getDontKnow.bind(this);
        this.onInput = this.onInput.bind(this);
        this.onCheck = this.onCheck.bind(this);
        this.getAnswer = this.getAnswer.bind(this);
    }

    getDontKnow() {
        if (this.props.showDontKnow)
            return (
                <DontKnow
                    checkBoxFunction={onCheck}
                    key={this.props.questionID}
                    checked={this.props.showDontKnowBox}
                />
            );

        return null;
    }

    /*
     * Record new response into localStorage, response has been validated
     * if this callback is fired
     */
    onInput(value, index) {

        console.log('Hey', index, value);
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');

        var answers = [{
            'response': value,
            'response_type': 'dont_know'
        }];

        survey[this.props.questionID] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

    }

    /*
     * Clear localStorage when dont know is checked
     * Call checkBoxFunction if supplied
     *
     * @event: click event on checkbox
     */
    onCheck(event) {
        // Clear responses
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        survey[this.props.questionID] = [];
        localStorage[this.props.surveyID] = JSON.stringify(survey);

        if (this.props.checkBoxFunction) {
            this.props.checkBoxFunction(event);
        }
    }

    /*
     * Get default value for an input at a given index from localStorage
     */
    getAnswer(questionID) {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[questionID] || [];
        return answers[0] && answers[0].response_type === 'dont_know' && answers[0].response || null;
    }


    render(){
        console.log('renderin!', this.props)
        let FooterClasses = 'bar bar-standard bar-footer';
        if (this.props.showDontKnow)
            FooterClasses += ' bar-footer-extended';
        if (this.props.showDontKnowBox)
            FooterClasses += ' bar-footer-extended bar-footer-super-extended';

        let self = this;
        return (
            <div className={FooterClasses}>
                <BigButton text={self.props.buttonText}
                type={self.props.buttonType}
                buttonFunction={self.props.buttonFunction} />
                { self.getDontKnow() }
                { self.props.showDontKnowBox ?
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
    
};
