'use strict';

import React from 'react';
import utils from './../utils.js';
import { orm } from './../redux/models.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { addLogic, updateLogic, updateQuestion } from './../redux/actions.babel.js'; 


function Logic(props) {

    function logicHandler(bound, event) {
        console.log('calling logic handler', bound);
        if (Object.keys(props.logic).length===0 && props.logic.constructor===Object) {
            let newLogic = {id: props.id, question: props.id, [bound]: event.target.value};
            console.log('newLogic', newLogic);
            props.addLogic(newLogic);
        } else {
            console.log('updating');
            props.updateLogic({id: props.id, [bound]: event.target.value});
        }
    }

    function renderFacility() {
        return(
            <div className="add-section">
                <div className="logic-input-container">
                    <label htmlFor="north" className="logic-label">North</label>
                    <input id="north"
                        className="logic-input"
                        onBlur={logicHandler.bind(null, 'nlat')} 
                        readOnly={props.saved}
                    />
                    <label htmlFor="west" className="logic-label">West</label>
                    <input id="west"
                        className="logic-input"
                        onBlur={logicHandler.bind(null, 'wlng')}
                        readOnly={props.saved}
                    />
                </div>
                <div className="logic-input-container">
                    <label htmlFor="south" className="logic-label">South</label>
                    <input id="south"
                        className="logic-input"
                        onBlur={logicHandler.bind(null, 'slat')}
                        readOnly={props.saved}
                    />
                    <label htmlFor="east" className="logic-label">East</label>
                    <input id="east"
                        className="logic-input"
                        onBlur={logicHandler.bind(null, 'elng')}
                        readOnly={props.saved}
                    />
                </div>
            </div>
        );
    }

    function renderMinMax() {
        return(
            <div style={{marginTop: "20px", display: "inline-block", padding: "0px 35px"}}>
                <label className="logic-label">Min:</label>
                <input className="logic-input" onBlur={logicHandler.bind(null, "min")}/>
                <label className="logic-label">Max:</label>
                <input className="logic-input" onBlur={logicHandler.bind(null, "max")}/>
            </div>
        );
    }


    return(
        <div className="title-group">
            <div style={{padding: "0px 15px"}}>
                <label htmlFor="question-title" className="col-form-label title">Bounds:</label>
            </div>
            {(props.type_constraint==="integer" ||
                props.type_constraint==="date" ||
                props.type_constraint==="decimal" ||
                props.type_constraint==="timeStamp") &&
                renderMinMax()
            }
            {(props.type_constraint==="facility") &&
                renderFacility()
            }
        </div>
    );
}


function mapStateToProps(state, ownProps){
    console.log('logic', state, ownProps);
    const session = orm.session(state.orm);
    console.log('ownProps', session.Question);
    console.log('session Logic', session.Logic);
    let questionLogic = session.Question.withId(ownProps.id).logic;
    console.log('questionLogic', questionLogic);
    let logic = questionLogic ? logic = Object.assign({}, questionLogic.ref) : {};
    console.log('logic', logic);
    return {
        logic: logic,
        id: ownProps.id
    };
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addLogic: addLogic,
        updateLogic: updateLogic,
        updateQuestion: updateQuestion}, 
        dispatch
    );
}

export default connect(mapStateToProps, matchDispatchToProps)(Logic);
