import React from 'react';

/*
 * Title component
 *
 * props:
 *  @title: Title text to render in content
 *  @message: 'hint' text to render in content
 */
export default function(props) {
    return (
        <div className="content-padded">
            <h3>{props.title}</h3>
            <p>{props.message}</p>
        </div>
    );
};
