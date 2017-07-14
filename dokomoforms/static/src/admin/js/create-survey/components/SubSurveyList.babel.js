'use strict';

import React from 'react';
import SubSurveyListItem from './SubSurveyListItem.babel.js';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { subSurveySelector } from './../redux/selectors.babel.js';
import { orm } from './../redux/models.babel.js';


function SubSurveyList(props) {

	// constructor(props) {
 //        super(props);

 //        this.viewSubSurveyHandler = this.viewSubSurveyHandler.bind(this);
 //        this.listSubSurveys = this.listSubSurveys.bind(this);
 //    }

    // componentWillMount() {
    //     console.log('ssl', this.props)
    // 	if (!this.props.sub_surveys || !this.props.sub_surveys.length) {
    // 		this.props.addSubSurvey();
    // 	}
    // }


    function listSubSurveys() {
    	// let self = this;
    	console.log('listSubSurveys')
    	let subList = [];
    	let renderList = [];
    	if (props.sub_surveys) {
    		console.log('it has subsurveys', props)
    		console.log(props)
    		subList = subList.concat(props.sub_surveys)
    	}
    	if (subList.length > 0) {
    		console.log('subList', subList)
    		let sub_survey;
    		subList.forEach(function(sub) {
		        sub_survey = sub
		        console.log('sub_survey', sub_survey)
		        renderList.push(
		            <SubSurveyListItem
                        parentQuestion={props.question_id}
		            	key={sub_survey.id}
		                sub_survey_id={sub_survey.id}
		                type_constraint={props.type_constraint}
		                choices={props.choices}
		            />
		        )
                renderList.push(<hr />)
			})
    	}
    	console.log(renderList);
        renderList.splice(-1, 1)
		return renderList;
    }

    function goToSubSurvey(survey_id) {
    	console.log('props', props)
    	console.log('go to subsurvey', survey_id)
    	props.goToSubSurvey(survey_id)
    }

	// render() {
		console.log('from subsurvey', props)
		return(
            <div className="title-group">
                <div className="sub-survey-list">
                    <label style={{fontSize: "25px"}}>SubSurvey List</label>
                    <div className="sub-survey-list-items" style={{margin: "10px 20px"}}>
                        {listSubSurveys()}
                    </div>
                </div>
            </div>
		)
	// }
}


function mapStateToProps(state, ownProps){


	console.log('state', ownProps)
    let choices = null;
    if (ownProps.type_constraint==='multiple_choice') {
        console.log('sublist choices')
        const session = orm.session(state.orm);
        console.log('ownProps', ownProps)

        console.log('state dot orm', 'subsurveylist')
        console.log(session.Question)

        choices = session.Question.withId(ownProps.question_id).multiple_choices;

        if (choices) choices = choices.toRefArray();

        console.log('the choices', choices);

    };

    return {
        choices: choices
    };
}


export default connect(mapStateToProps)(SubSurveyList);
