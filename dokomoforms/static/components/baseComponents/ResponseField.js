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
            case "location":
                return "number"
            case "timestamp":
            case "time":
                return "time"
            case "date":
                return "date"
            default:
                return "text"
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
                val = year+"-"+(month)+"-"+(day);
                if(isNaN(year) || isNaN(month) || isNaN(day))  {
                    val = null;
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
            this.props.onInput(this.props.index, value);
    },

    render: function() {
        return (
                <div className="input_container">
                    <input 
                        type={this.getResponseType()} 
                        placeholder="Please provide a response." 
                        onChange={this.onChange}
                        defaultValue={this.props.initValue}
                     >
                     {this.props.showMinus ? 
                        <span 
                            onClick={this.props.buttonFunction.bind(null, this.props.index)} 
                            className="icon icon-close question__minus">
                        </span>
                        : null}
                    </input>
                 </div>
               )
    }
});
