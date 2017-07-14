import React from 'react';
import utils from './../utils.js';
import { orm } from './../redux/models.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { addLogic, updateLogic, deleteLogic, updateQuestion } from './../redux/actions.babel.js'; 


function Logic(props) {

    let minVal = "";
    let maxVal = "";
    let nlatVal = "";
    let wlngVal = "";
    let slatVal = "";
    let elngVal = "";

    let current_type_constraint = current_type_constraint || null;

    console.log('current type 1', current_type_constraint, props.type_constraint)

    if (current_type_constraint!==props.type_constraint && 
        props.logic.length) {
        console.log('not the same type at logic');
        props.deleteHandler()
    }

    current_type_constraint = props.type_constraint;
    console.log('current type 2', current_type_constraint, props.type_constraint)

    function logicHandler(bound, event) {
        // console.log('calling logic handler', bound);
        if (Object.keys(props.logic).length===0 && props.logic.constructor===Object) {
            let newLogic = {id: props.id, question: props.id, [bound]: event.target.value};
            props.addLogic(newLogic);
        } else {
            props.updateLogic({id: props.id, [bound]: event.target.value});
        }
    }

    function deleteHandler() {
        let minVal = "";
        let maxVal = "";
        let nlatVal = "";
        let wlngVal = "";
        let slatVal = "";
        let elngVal = "";
        props.deleteLogic(props.logic.id);
    }

    function renderFacility() {
        return(
            <div>
                <div className="logic-input-container">
                    <label htmlFor="north" className="logic-label">North</label>
                    <input id="north"
                        className="logic-input"
                        ref={(input)=>{ nlatVal = input; }}
                        value={props.logic.nlatVal || nlatVal}
                        onChange={logicHandler.bind(null, "nlat")}
                    />
                    <label htmlFor="west" className="logic-label">West</label>
                    <input id="west"
                        className="logic-input"
                        ref={(input)=>{ wlngVal = input; }}
                        value={props.logic.wlngVal || wlngVal}
                        onChange={logicHandler.bind(null, "wlng")}
                    />
                </div>
                <div className="logic-input-container">
                    <label htmlFor="south" className="logic-label">South</label>
                    <input id="south"
                        className="logic-input"
                        ref={(input)=>{ slatVal = input; }}
                        value={props.logic.slatVal || slatVal}
                        onChange={logicHandler.bind(null, "slat")}
                    />
                    <label htmlFor="east" className="logic-label">East</label>
                    <input id="east"
                        className="logic-input"
                        ref={(input)=>{ elngVal = input; }}
                        value={props.logic.elngVal || elngVal}
                        onChange={logicHandler.bind(null, "elng")}
                    />
                </div>
            </div>
        );
    }

    function renderMinMax() {
        console.log('minmax', props.logic)
        return(
            <div className="logic-input-container">
                <label className="logic-label">Min:</label>
                <input className="logic-input"
                    ref={(input)=>{ minVal = input; }}
                    value={props.logic.min || minVal}
                    onChange={logicHandler.bind(null, "min")}
                    />
                <label className="logic-label">Max:</label>
                <input className="logic-input"
                    ref={(input)=>{ maxVal = input; }}
                    value={props.logic.max || maxVal}
                    onChange={logicHandler.bind(null, "max")}
                />
            </div>
        );
    }


    return(
        <div className="add-section">
            <div className="title-group">
                <div className="logic-header">
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
                <button
                    onClick={deleteHandler}>
                    delete bounds
                </button>
            </div>
        </div>
    );
}


function mapStateToProps(state, ownProps){
    console.log('logic', state, ownProps);
    const session = orm.session(state.orm);
    console.log('ownProps', ownProps);
    console.log('session Logic', session.Logic);
    let questionLogic = session.Question.withId(ownProps.id).logic;
    console.log('questionLogic', questionLogic);
    let logic = questionLogic ? logic = Object.assign({}, questionLogic.ref) : {};
    console.log('logic', logic.length);
    return {
        logic: logic,
        id: ownProps.id
    };
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addLogic: addLogic,
        updateLogic: updateLogic,
        deleteLogic: deleteLogic,
        updateQuestion: updateQuestion}, 
        dispatch
    );
}

export default connect(mapStateToProps, matchDispatchToProps)(Logic);
