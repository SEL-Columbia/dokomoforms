import React from 'react';

/*
 * Message component
 *
 * @text: text to render
 */
export default function(props) {
    var textClass = props.classes;
    return (
        <div className='content-padded'>
            <p className={textClass}>{props.text}</p>
        </div>
    );
});

