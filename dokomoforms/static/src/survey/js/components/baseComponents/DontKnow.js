import React from 'react';

/*
 * Don't know component
 *
 * props:
 *  @checkBoxFunction: What to do on click event
 */
export default function(props){
    return (
        <div className='question__btn__other'>
            <input
                onClick={props.checkBoxFunction}
                type='checkbox'
                id='dont-know'
                name='dont-know'
                defaultChecked={props.checked}
            />
            <label htmlFor='dont-know'>I don't know the answer</label>
        </div>
    );
};

