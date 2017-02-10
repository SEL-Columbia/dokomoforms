import React from 'react';
import utils from './../utils.js';
import ReactDOM from 'react-dom';
import {orm} from './../redux/models.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {addLogic, updateLogic} from './../redux/actions.babel.js'; 


class Logic extends React.Component {

    constructor(props) {

        super(props);

        this.renderFacility = this.renderFacility.bind(this);
        this.renderMinMax = this.renderMinMax.bind(this);
        this.logicHandler = this.logicHandler.bind(this);

    }

    renderFacility() {
        return(
            <div className="form-group" style={{backgroundColor:'#02c39a'}}>
                <div className="row">
                    <label htmlFor="north" className="col-xs-2 col-form-label">North</label>
                    <div className="col-xs-10">
                        <input id="north" className="form-control question-title" onBlur={this.logicHandler.bind(null, 'nlat')} readOnly={this.props.saved}/>
                    </div>
                </div>
                <div className="row">
                    <label htmlFor="south" className="col-xs-2 col-form-label">South</label>
                    <div className="col-xs-10">
                        <input id="south" className="form-control question-title" onBlur={this.logicHandler.bind(null, 'slat')} readOnly={this.props.saved}/>
                    </div>
                </div>
                <div className="row">
                    <label htmlFor="west" className="col-xs-2 col-form-label">West</label>
                    <div className="col-xs-10">
                        <input id="west" className="form-control question-title" onBlur={this.logicHandler.bind(null, 'wlng')} readOnly={this.props.saved}/>
                    </div>
                </div>
                <div className="row">
                    <label htmlFor="east" className="col-xs-2 col-form-label">East</label>
                    <div className="col-xs-10">
                        <input id="east" className="form-control question-title" onBlur={this.logicHandler.bind(null, 'elng')} readOnly={this.props.saved}/>
                    </div>
                </div>
            </div>
        )
    }


    logicHandler(bound, event) {
        console.log('calling logic handler');
        const logic = {id: this.props.id, question: this.props.id, [bound]: event.target.value};
        if (this.props.logic) this.props.updateLogic(logic);
        else this.props.addLogic(logic);
    }

    renderMinMax() {
        return(
            <div>
                {(this.props.type_constraint=="integer" ||
                    this.props.type_constraint=="date" ||
                    this.props.type_consrtaint=="decimal") &&
                    <div className="form-group" style={{backgroundColor:'#02c39a'}}>
                        <div className="row">
                            <label htmlFor="north" className="col-xs-2 col-form-label">Min</label>
                            <div className="col-xs-10">
                                <input id="north" className="form-control question-title" onBlur={this.logicHandler.bind(null, 'min')} readOnly={this.props.saved}/>
                            </div>
                        </div>
                        <div className="row">
                            <label htmlFor="south" className="col-xs-2 col-form-label">Max</label>
                            <div className="col-xs-10">
                                <input id="south" className="form-control question-title" onBlur={this.logicHandler.bind(null, 'max')} readOnly={this.props.saved}/>
                            </div>
                        </div>
                </div>
                }
            </div>
        )
    }


    render(){
        return(
            <div>

                {(this.props.type_constraint=="integer" ||
                this.props.type_constraint=="date" ||
                this.props.type_constraint=="decimal") &&
                this.renderMinMax()
                }

                {(this.props.type_constraint=="facility") &&
                this.renderFacility()
                }
            
            </div>
        )
    }
}



function mapStateToProps(state, ownProps){
    console.log('here', ownProps);
    console.log(state);
    const session = orm.session(state.orm);
    console.log('ownProps', session.Question);
    console.log('state dot orm', session.Logic);
    console.log(session.Logic.all().toRefArray());
    const id = ownProps.id;
    let logic;
    logic = session.Question.withId(id).logic;
    if (logic) logic = logic.ref;
    console.log('question', session.Question.withId(id))
    console.log('logic', logic);
    return {
        logic: logic
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addLogic: addLogic,
        updateLogic: updateLogic}, 
        dispatch
    )
}

export default connect(mapStateToProps, matchDispatchToProps)(Logic);