import React from'react';

/*
 * Big 'ol button
 *
 * props:
 *  @type: Type of button (class name from ratchet usually) defaults to btn-primary
 *  @buttonFunction: What to do on click events
 *  @text: Text of the button
 */
export default function(props){
    var buttonClasses = 'btn btn-block navigate-right page_nav__next';
    if (props.type) {
        buttonClasses += ' ' + props.type;
    } else {
        buttonClasses += ' btn-primary';
    }

    return (
        <div className='bar-padded'>
            <button onClick={props.buttonFunction} className={buttonClasses}>
                {props.text}
            </button>
        </div>
   );
};

