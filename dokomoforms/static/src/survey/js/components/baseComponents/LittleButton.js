import React from'react';

/*
 * Little weeny button
 *
 * props:
 *  @type: Type of button (class name from ratchet usually) defaults to btn-primary
 *  @buttonFunction: What to do on click events
 *  @text: Text of the button
 *  @icon: Icon if any to show before button text
 *  @disabled: Whether or not the button should be disabled
 */
export default function(props){
    render() {
        var iconClass = 'icon icon-inline-left ' + props.icon;
        var classes = 'btn ';
        classes += props.extraClasses || '';
        return (
            <div className='content-padded'>
                <button className={classes}
                    disabled={props.disabled}
                    onClick={props.buttonFunction} >

                    {props.icon ? <span className={iconClass}></span> : null }
                    {props.text}
                </button>
            </div>
       );
    }
};

