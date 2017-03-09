import React from 'react';
import moment from 'moment';

/*
 * ResponseField component
 * Main input field component, handles validation
 *
 * props:
 *  @type: question type constraint, sets the input type to it, defaults to text
 *  @logic: dictionary containing logic to enforce
 *  @onInput: What to do on valid input
 *  @index: What index value to send on valid input (i.e position in array of fields)
 *  @showMinus: Show the 'X' on the input
 *  @buttonFunction: What to do on 'X' click event, index value is bound to this function
 *  @placeholder: Placeholder text for input, defaults to 'Please provide a response'
 *  @initValue: Initial value for the input field
 */
export default function(props) {

    // Determine the input field type based on props.type
    function getResponseType() {
        var type = props.type;
        switch (type) {
            case 'integer':
            case 'decimal':
                return 'number';
            case 'timestamp':
                return 'datetime-local';
            case 'time':
                return 'time';
            case 'date':
                return 'date';
            case 'email':
                return 'email';
            default:
                return 'text';
        }
    }

    // Determine the input field step based on props.type
    function getResponseStep() {
        var type = props.type;
        switch (type) {
            case 'decimal':
                return 'any';
            case 'timestamp':
                return '1';
            default:
                return null;
        }
    }

    /*
     * Validate the answer based on props.type
     *
     * @answer: The response to be validated
     */
    function validate(answer) {
        var type = props.type;
        var logic = props.logic;
        var val = null;
        switch (type) {
            case 'integer':
                val = parseInt(answer);
                if (isNaN(val)) {
                    val = null;
                    break;
                }

                if (logic && logic.min && typeof logic.min === 'number') {
                    if (val < logic.min) {
                        val = null;
                    }
                }

                if (logic && logic.max && typeof logic.max === 'number') {
                    if (val > logic.max) {
                        val = null;
                    }
                }

                break;
            case 'decimal':
                val = parseFloat(answer);
                if (isNaN(val)) {
                    val = null;
                }

                if (logic && logic.min && typeof logic.min === 'number') {
                    if (val < logic.min) {
                        val = null;
                    }
                }

                if (logic && logic.max && typeof logic.max === 'number') {
                    if (val > logic.max) {
                        val = null;
                    }
                }

                break;
            case 'date':
                var resp = new Date(answer);
                var day = ('0' + resp.getDate()).slice(-2);
                var month = ('0' + (resp.getMonth() + 1)).slice(-2);
                var year = resp.getFullYear();
                val = answer; //XXX Keep format?
                if (isNaN(year) || isNaN(month) || isNaN(day)) {
                    val = null;
                }


                if (logic && logic.min && !isNaN((new Date(logic.min)).getDate())) {
                    if (resp < new Date(logic.min)) {
                        val = null;
                    }
                }

                if (logic && logic.max && !isNaN((new Date(logic.max)).getDate())) {
                    if (resp > new Date(logic.max)) {
                        val = null;
                    }
                }

                break;
            case 'timestamp':
                //TODO: enforce min/max
                val = moment(answer).toDate();
                console.log('val: ', val);
                break;
            case 'time':
            default:
                if (answer) {
                    val = answer;
                }
        }

        return val;

    }

    /*
     * Handle change event, validates on every change
     * fires props.onInput with validated value OR null
     *
     * @event: Change event
     */
    function onChange(event) {
        var value = validate(event.target.value);
        var input = event.target;
        input.setCustomValidity('');

        if (value === null) {
            window.target = event.target;
            input.setCustomValidity('Invalid field.');
        }

        if (props.onInput)
            props.onInput(value, props.index);
    }

    return (
        <div className='input_container'>
            <input
                type={getResponseType()}
                step={getResponseStep()}
                placeholder={props.placeholder || 'Please provide a response.'}
                onChange={onChange}
                defaultValue={props.initValue}
                disabled={props.disabled}
             >
             {props.showMinus ?
                <span
                    onClick={props.buttonFunction.bind(null, props.index)}
                    disabled={props.disabled}
                    className='icon icon-close question__minus'>
                </span>
                : null}
            </input>
        </div>
    );
});
