import React from 'react';
import utils from './../utils.js';
import ReactDOM from 'react-dom';

class FacilityLogic extends React.Component {

    constructor(props) {

        super(props);

        this.logicHandler = this.logicHandler.bind(this);

        this.state = {
            nlat: undefined,
            slat: undefined,
            wlng: undefined,
            elng: undefined
        }
    }

    logicHandler(coordinate, event) {
        this.setState({[coordinate]: event.target.value}, function(){
            console.log(this.state);
        });
    }

    render() {
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
}

class MinMaxLogic extends React.Component {

    constructor(props) {

        super(props);

        this.logicHandler = this.logicHandler.bind(this);

        this.state = {
            min: undefined,
            max: undefined
        }
    }

    logicHandler(bound, event) {
        this.setState({[bound]: event.target.value}, function(){
            console.log(this.state);
        });
    }

    render() {
        return(
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
        )
    }
}


export { FacilityLogic, MinMaxLogic };

