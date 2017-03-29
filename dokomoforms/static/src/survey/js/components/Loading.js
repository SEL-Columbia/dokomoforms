import React from 'react';

/*
 * Loading component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 */
export default function(props) {
    return (
        <div className="loading-overlay">
            <div className="loading-content">
                <img src="/static/dist/survey/img/loading.gif" />
                <br/>
                <p>{props.message}</p>
            </div>
        </div>
    );
};
