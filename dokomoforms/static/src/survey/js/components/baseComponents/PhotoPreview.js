import React from 'react';

/*
 * PhotoPreview component
 *
 * Displays a preview of the Photo
 *
 * props:
 *  @onClose: What to do when the close button is pressed
 *  @onDelete: What to do when the delete button is pressed
 *  @url: The URL of the photo to display
 */
export default function(props) {
    const divStyle = {
        backgroundImage: 'url(' + props.url + ')'
    };

    return (
        <div className="photo_preview_container dark_overlay" style={divStyle} >
            <button className="btn btn-photo-close" onClick={props.onClose}>
                <span className="icon icon-close" ></span>
            </button>

            <button className="btn btn-photo-delete" onClick={props.onDelete}>
                <span className="icon icon-trash"></span> Delete
            </button>
         </div>
    );
};
