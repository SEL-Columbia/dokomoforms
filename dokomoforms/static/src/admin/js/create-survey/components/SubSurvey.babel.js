import React from 'react';
import NodeList from './NodeList.babel.js';
import BucketsList from './BucketsList.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { updateCurrentSurvey, updateSurvey } from './../redux/actions.babel.js';
import { parentSurveySelector, parentQuestionTitleSelector, nodeSelector, surveySelector } from './../redux/selectors.babel.js';


function SubSurvey(props) {

    if (!props.survey.buckets && (props.survey.repeatable!=="true")) {
        props.updateSurvey({id: props.survey.id, repeatable: "true"})
    }

    const parentQuestion = props.parentQuestionTitle[props.default_language] || "this question has not been defined!"

    if (props.survey.repeatable===undefined) {
        // if (!props.buckets) props.updateSurvey({id: props.survey.id, repeatable: "true"});
        // else props.updateSurvey({id: props.survey.id, repeatable: "false"});
    }

    function viewPreviousSurvey(){
        console.log('view previous survey', props.parentSurveyId);
        props.updateCurrentSurvey(props.parentSurveyId);
    }

    function toggleRepeatable(event){
        console.log(event.target.value);
        props.updateSurvey({id: props.survey.id, repeatable: event.target.value});
    }

    // render() {
        console.log('from the new subsurvey view', props)

        return (
            <div className="container">
                <div className="col-lg-8 survey center-block">
                    <div className="survey-header">
                        Create a Sub Survey
                    </div>
                    <div className="survey-section">
                        <div className="survey-group">
                            <span id="parent-question-header">Parent Question: </span>
                            <span id="parent-question-text">"{parentQuestion}"</span>
                        </div>
                        <hr />
                        <div className="survey-group">
                            <div className="survey-double-column">
                                <label className="col-form-label double-column-label">Buckets:</label>
                                {(!props.survey.buckets || !props.survey.buckets.length) &&
                                    <div id="buckets-message">
                                        There are no buckets!
                                        <p />
                                        This sub-survey must be repeatable.
                                        <p />
                                        The number of times this sub-survey will repeat
                                        is based off of the survey receipient's answer
                                        to the parent question.
                                    </div>
                                }
                                {(props.survey.buckets) &&
                                    <BucketsList 
                                        buckets={props.survey.buckets}
                                        type_constraint={props.survey.buckets[0].bucket_type}
                                        deleteBucket={null}
                                    />
                                }
                            </div>
                            <div className="survey-double-column">
                                <label className="col-form-label double-column-label">Repeatable:</label>
                                <div className="multiple-response">
                                    <div className="allow-multiple">
                                        <input type="radio"
                                                name="repeatable"
                                                disabled={!props.survey.buckets}
                                                value={"true"}
                                                onChange={toggleRepeatable}
                                                checked={props.survey.repeatable==="true"}
                                        />
                                        <label>Yes</label>
                                    </div>
                                    <div className="allow-multiple">
                                        <input type="radio"
                                                name="repeatable"
                                                disabled={!props.survey.buckets}
                                                value={"false"}
                                                onChange={toggleRepeatable}
                                                checked={props.survey.repeatable==="false"}/>
                                        <label>No</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div>
                        {/*
                        <NodeList
                            repeatable={props.survey.repeatable}
                            key={props.survey.id}
                            submitted={props.submitted}
                            survey_id={props.survey.id}
                            survey_nodes={props.nodes}
                            languages={props.languages}
                        />
                        */}
                        <NodeList
                            repeatable={props.survey.repeatable}
                            languages={props.languages}
                        />
                    </div>
                </div>
            </div>
        );
}


function mapStateToProps(state){
    console.log('map state subsurvey', state);
    return {
        parentQuestionTitle: parentQuestionTitleSelector(state),
        parentSurveyId: parentSurveySelector(state),
        survey: surveySelector(state),
        default_language: state.default_language
    };
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({updateCurrentSurvey: updateCurrentSurvey,
                                updateSurvey: updateSurvey}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(SubSurvey);
