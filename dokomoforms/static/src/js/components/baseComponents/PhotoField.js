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
     *
     * TODO: implement photo validation, if necessary...
     */
    validate: function(answer) {
        return true;
    },

    /*
     * Handle change event, validates on every change
     * fires props.onInput on validation success
     *
     * @event: Change event
     */
    // onChange: function(event) {

    // },

    render: function() {
        return (
                <div className="photo_container">
                    <img
                        className="photo_input"
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
               );
    }
});
