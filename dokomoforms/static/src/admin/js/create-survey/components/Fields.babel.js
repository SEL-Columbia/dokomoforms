import React from 'react';

function Fields(props) {

    console.log('fields!', props)
    
    let showBoundsButton = false;
    let showSubSurveyButton = true;

    if (props.type_constraint==='integer' ||
        props.type_constraint==='decimal' ||
        props.type_constraint==='date' ||
        props.type_constraint==='facility') {
        showBoundsButton = true;
    }

    console.log(showBoundsButton, showSubSurveyButton)

    return(
        <div className="question-bar">
        <div className="arrows" style={{width: "100%", height: "20px", marginBottom: "8px"}}>
            {props.showHint &&
                <div className="arrow-up" style={{display: "inline", position: "relative", left: "32px"}}></div>
            }
            {props.showLogic &&
                <div className="arrow-up" style={{display: "inline", position: "relative", left: "110px"}}></div>
            }
            {props.showSubSurveys &&
                <div className="arrow-up" style={{display: "inline", position: "relative", left: "235px"}}></div>
            }
        </div>
            <div className="fields">
                <div className="btn-group" role="group" aria-label="...">
                    <button type="button" onClick={props.toggleField.bind(null, 'showHint')} id="hint-button" className="btn btn-default field-button">Add Hint</button>
                    <button type="button" onClick={props.toggleField.bind(null, 'showLogic')} id="bounds-button" className="btn btn-default field-button" disabled={!showBoundsButton}>Add Bounds</button>
                    <button type="button" onClick={props.addSubSurvey} className="btn btn-default field-button" id="subsurvey-button" disabled={!showSubSurveyButton}>Add Sub-Survey</button>
                </div>
                <button type="button" onClick={props.deleteNode} className="btn btn-default" id="delete-node-btn">Delete</button>
            </div>
        </div>
    )

}

export default Fields;