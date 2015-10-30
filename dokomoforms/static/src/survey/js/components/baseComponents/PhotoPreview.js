var React = require('react');

/*
 * ResponseField component
 * Main input field component, handles validation
 *
 * props:
 *  @onInput: What to do on valid input
 *  @index: What index value to send on valid input (i.e position in array of fields)
 *  @showRetake: Show the 'retake' button
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
        var divStyle = {
            backgroundImage: 'url(' + this.props.url + ')'
        };

        return (
            <div className="photo_preview_container dark_overlay" style={divStyle} >
                <button className="btn btn-photo-close" onClick={this.props.onClose}>
                    <span className="icon icon-close" ></span>
                </button>

                <button className="btn btn-photo-delete" onClick={this.props.onDelete}>
                    <span className="icon icon-trash"></span> Delete
                </button>
             </div>
        );
    }
});
