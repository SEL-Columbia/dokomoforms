import React from 'react';
import ResponseField from './ResponseField.js';

/*
 * Array of ResponseField
 *
 * Refer to ResponseField for use
 * XXX Remove Component
 */
export default function(props) {
    var children = Array.apply(null, {length: props.childCount});
    var self = this;
    return (
            <div>
            {children.map(function(child, idx) {
                return (
                    <ResponseField
                        buttonFunction={props.buttonFunction}
                        onInput={props.onInput}
                        type={props.type}
                        key={idx + 1}
                        index={idx}
                        showMinus={props.childCount > 1}
                    />
                );
            })}
            </div>
    );
};

