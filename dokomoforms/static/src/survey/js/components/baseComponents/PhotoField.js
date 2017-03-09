import React from 'react';
import PhotoPreview from './PhotoPreview';

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
export default class PhotoField extends React.Component {

    constructor(props) {
        super(props);

        this.showPreview = this.showPreview.bind(this);
        this.hidePreview = this.hidePreview.bind(this);
        this.onDelete = this.onDelete.bind(this);

        this.state = {
            showPreview: false
        }
    }

    showPreview() {
        this.setState({
            showPreview: true
        });
    }

    hidePreview() {
        this.setState({
            showPreview: false
        });
    }

    onDelete() {
        this.hidePreview();
        this.props.buttonFunction(this.props.index);
    }

    render() {
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
};
