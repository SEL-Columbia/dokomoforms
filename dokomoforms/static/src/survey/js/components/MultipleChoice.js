import React from 'react';
import Select from './baseComponents/Select.js';

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
export default class MultipleChoice extends React.Component {

    constructor(props) {
        super(props);

        this.update = this.update.bind(this);
        this.onSelect = this.onSelect.bind(this);
        this.onInput = this.onInput.bind(this);
    }

    /*
     * Hack to force react to update child components
     * Gets called by parent element through 'refs' when state of something changed 
     * (usually localStorage)
     */
    update(){console.log('forced update')};

    /*
     * Record all selected options into localStorage
     */
    onSelect(values) {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = [];
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
    }

    /*
     * Record other response into existing slot of answer object in localStorage
     * Callback is only called on validated input
     */
    onInput(value) {
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

    }

    /*
     * Get all selected options from localStorage
     */
    getSelection() {
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
    }

    /*
     * Get other response if any from localStorage 
     */
    getAnswer() {
        console.log('get answer from mc', this.props, this)
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
    }

    render(){

        var self = this;
        var choices = self.props.question.choices.map(function(choice) {
            return { 
                'value': choice.choice_id, 
                'text': choice.choice_text[self.props.language] 
            }
        });

        // Key is used as hack to rerender select on dontKnow state change
        console.log('props', self.props)
        console.log('choices', choices)
        return (<Select 
                    key={self.props.disabled}
                    choices={choices}
                    withOther={self.props.question.allow_other}
                    multiSelect={self.props.question.allow_multiple}
                    disabled={self.props.disabled}
                    initValue={self.getAnswer()} 
                    initSelect={self.getSelection()} 
                    onSelect={self.onSelect}
                    onInput={self.onInput}
                />)
    }
};
