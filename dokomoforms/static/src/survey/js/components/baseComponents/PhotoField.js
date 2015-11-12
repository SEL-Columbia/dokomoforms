var React = require('react'),
    PhotoPreview = require('./PhotoPreview');

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
    getInitialState: function() {
        return {
            showPreview: false
        };
    },

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

    showPreview: function() {
        console.log('showPreview');
        this.setState({
            showPreview: true
        });
    },

    hidePreview: function() {
        console.log('hidePreview');
        this.setState({
            showPreview: false
        });
    },

    onDelete: function() {
        this.hidePreview();
        this.props.buttonFunction(this.props.index);
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
        var preview;
        if (this.state.showPreview) {
            preview = <PhotoPreview
                url={this.props.initValue}
                onDelete={this.onDelete}
                onClose={this.hidePreview}
            />;
        }
        return (
            <span>
                {preview}
                <div className="photo_container" onClick={this.showPreview}>
                    { this.props.initValue ?
                        <img
                            className="photo_input"
                            src={this.props.initValue}
                            disabled={this.props.disabled}
                         /> :
                         ''
                    }
                </div>
            </span>
        );
    }
});
