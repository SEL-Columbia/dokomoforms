var React = require('react'),
    createReactClass = require('create-react-class'),
    moment = require('moment');

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
module.exports = createReactClass({
    getInitialState: function() {
        return {};
    },

    // Determine the input field type based on props.type
    getResponseType: function() {
        var type = this.props.type;
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
    },

    // Determine the input field step based on props.type
    getResponseStep: function() {
        var type = this.props.type;
        switch (type) {
            case 'decimal':
                return 'any';
            case 'timestamp':
                return '1';
            default:
                return null;
        }
    },

    /*
     * Validate the answer based on props.type
     *
     * @answer: The response to be validated
     */
    validate: function(answer) {
        var type = this.props.type;
        var logic = this.props.logic;
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

    },

    /*
     * Handle change event, validates on every change
     * fires props.onInput with validated value OR null
     *
     * @event: Change event
     */
    onChange: function(event) {
        var value = this.validate(event.target.value);
        var input = event.target;
        input.setCustomValidity('');

        if (value === null) {
            window.target = event.target;
            input.setCustomValidity('Invalid field.');
        }

        if (this.props.onInput)
            this.props.onInput(value, this.props.index);
    },

    render: function() {
        return (
            <div className='input_container'>
                <input
                    type={this.getResponseType()}
                    step={this.getResponseStep()}
                    placeholder={this.props.placeholder || 'Please provide a response.'}
                    onChange={this.onChange}
                    defaultValue={this.props.initValue}
                    disabled={this.props.disabled}
                />
                {this.props.showMinus ?
                    <span
                        onClick={this.props.buttonFunction.bind(null, this.props.index)}
                        disabled={this.props.disabled}
                        className='icon icon-close question__minus'>
                    </span>
                    : null}
            </div>
        );
    }
});
