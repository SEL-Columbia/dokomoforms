var React = require('react');

/*
 * ResponseField component
 * Main input field component, handles validation
 *
 * props:
 *  @onInput: What to do on valid input
 *  @index: What index value to send on valid input (i.e position in array of fields)
 *  @showMinus: Show the 'X' on the input
 *  @buttonFunction: What to do on 'X' click event, index value is bound to this function
 *  @initValue: Initial value for the input field
 */
module.exports = React.createClass({

    /*
     * Validate the answer based on props.type
     * 
     * @answer: The response to be validated
     */
    validate: function(answer) {
        return val;

    }, 

    /*
     * Handle change event, validates on every change
     * fires props.onInput on validation success
     *
     * @event: Change event
     */
    onChange(event) {
    },

    render: function() {
        return (
                <div className="input_container">
                    <img 
                        src={this.props.initValue}
                        disabled={this.props.disabled}
                     >
                     {this.props.showMinus ? 
                        <span 
                            onClick={this.props.buttonFunction.bind(null, this.props.index)} 
                            disabled={this.props.disabled}
                            className="icon icon-close question__minus">
                        </span>
                        : null}
                    </img>
                 </div>
               )
    }
});
