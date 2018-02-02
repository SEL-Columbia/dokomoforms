var React = require('react'),
    createReactClass = require('create-react-class'),
    PhotoPreview = require('./PhotoPreview');

/*
 * PhotoField component
 *
 * Displays a photo thumbnail.
 *
 * props:
 *  @onInput: What to do on valid input
 *  @index: What index value to send on valid input (i.e position in array of fields)
 *  @showRetake: Show the 'retake' button
 *  @buttonFunction: What to do on 'X' click event, index value is bound to this function
 *  @initValue: Initial value for the input field
 */
module.exports = createReactClass({
    getInitialState: function() {
        return {
            showPreview: false
        };
    },

    showPreview: function() {
        this.setState({
            showPreview: true
        });
    },

    hidePreview: function() {
        this.setState({
            showPreview: false
        });
    },

    onDelete: function() {
        this.hidePreview();
        this.props.buttonFunction(this.props.index);
    },

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
