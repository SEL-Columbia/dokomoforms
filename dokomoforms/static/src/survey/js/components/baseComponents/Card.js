import React from 'react';

/*
 * Card component
 *
 * props:
 *  @type: Card type (class name from ratchet usually) defaults to message-primary
 *  @msg: Array of messages, each element is placed on a new line. JSX accepted
 */
export default function(props) {
    var messageClass = 'message-box';
    if (props.type) {
        messageClass += ' ' + props.type;
    } else {
        messageClass += ' message-primary';
    }

    return (
        <div className='content-padded'>
            <div className={messageClass} >
            {props.messages.map(function(msg, idx) {
                return (
                        <span key={idx}> {msg} <br/> </span>
                    );
            })}
            </div>
        </div>
   );
};
