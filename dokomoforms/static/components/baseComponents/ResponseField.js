var React = require('react');

/*
 * ResponseField component
 * Main input field component, handles validation
 *
 * props:
 *  @type: question type constraint, sets the input type to it, defaults to text
 *  @onInput: What to do on valid input
 *  @index: What index value to send on valid input (i.e position in array of fields)
 *  @showMinus: Show the 'X' on the input
 *  @buttonFunction: What to do on 'X' click event, index value is bound to this function
 *  @placeholder: Placeholder text for input, defaults to 'Please provide a response'
 *  @initValue: Initial value for the input field
 */
module.exports = React.createClass({
    // Determine the input field type based on props.type
    getResponseType: function() {
        var type = this.props.type;
        console.log(type);
        switch(type) {
            case "integer":
            case "decimal":
                return "number"
            case "timestamp":
            case "time":
                return "time"
            case "date":
                return "date"
            case "email":
                return "email"
            default:
                return "text"
        }
    }, 

    // Determine the input field step based on props.type
    getResponseStep: function() {
        var type = this.props.type;
        console.log(type);
        switch(type) {
            case "decimal":
            case "location":
                return "any"
            default:
                return ""
        }
    }, 

    /*
     * Validate the answer based on props.type
     * 
     * @answer: The response to be validated
     */
    validate: function(answer) {
        var type = this.props.type;
        var val = null;
        switch(type) {
            case "integer":
                val = parseInt(answer);
                if (isNaN(val)) {
                    val = null;
                }
                break;
            case "decimal":
                val = parseFloat(answer);
                if (isNaN(val)) {
                    val = null;
                }
                break;
            case "date":
                var resp = new Date(answer);
                var day = ("0" + resp.getDate()).slice(-2);
                var month = ("0" + (resp.getMonth() + 1)).slice(-2);
                var year = resp.getFullYear();
                if(isNaN(year) || isNaN(month) || isNaN(day))  {
                    val = null;
                } else {
                    val = answer; //XXX Keep format?
                }
                break;
            case "timestamp":
            case "time":
            default:
              if (answer) {
                  val = answer;
              }
        }

        return val;

    }, 

    /*
     * Handle change event, validates on every change
     * fires props.onInput on validation success
     *
     * @event: Change event
     */
    onChange(event) {
        var value = this.validate(event.target.value);
        console.log(event.target.value);
        if (this.props.onInput && value !== null)
            this.props.onInput(value, this.props.index);
    },

    render: function() {
        return (
                <div className="input_container">
                    <input 
                        type={this.getResponseType()} 
                        step={this.getResponseStep()}
                        placeholder={this.props.placeholder || "Please provide a response."}
                        onChange={this.onChange}
                        defaultValue={this.props.initValue}
                        disabled={this.props.disabled}
                     >
                     {this.props.showMinus ? 
                        <span 
                            onClick={this.props.buttonFunction.bind(null, this.props.index)} 
                            disabled={this.props.disabled}
                            className="icon icon-close question__minus">
                        </span>
                        : null}
                    </input>
                 </div>
               )
    }
});
