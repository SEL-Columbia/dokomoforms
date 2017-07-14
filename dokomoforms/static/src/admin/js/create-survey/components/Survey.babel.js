import React from 'react';
import NodeList from './NodeList.babel.js';
import SurveyTitle from './subcomponents/SurveyTitle.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { updateSurvey } from './../redux/actions.babel.js';
import { surveySelector } from './../redux/selectors.babel.js';
import { orm } from './../redux/models.babel.js';


function Survey(props) {

    function updateTitle(language, event) {
        const titleObj = {};
        titleObj[language] = event.target.value;
        props.updateSurvey({id: props.survey.id, title: titleObj});
    }

    function changeSurveyType(event) {
        const target = event.target.getAttribute('value');
        props.updateSurvey({id: props.survey.id, survey_type: target});
    }
 
    function updateDefaultLanguage(event) {
        const prevDefaultLanguage = props.survey.default_language;
        const newDefaultLanguage = event.target.value;
        const updatedSurvey = {id: props.survey.id, default_language: newDefaultLanguage};
        if (props.survey.title) {
            updatedSurvey.title = {};
            updatedSurvey.title[newDefaultLanguage] = props.survey.title[prevDefaultLanguage];
        }
        props.updateSurvey(updatedSurvey);
    }

    // function addLanguage(language){
    //     let languageList = [];
    //     languageList = languageList.concat(this.state.languages);
    //     // possible add check for duplicate
    //     languageList.push(language);
    //     // this.setState({languages: languageList}, function(){
    //     //     console.log('language added', language, this.state.languages);
    //     // });
    // }

    console.log('survey component', props.survey)
    return (
        <div className="survey-container">
            <div className="survey center-block">
                <div className="survey-header">
                    Create a Survey
                </div>
                <div className="survey-section">
                    <SurveyTitle 
                        updateTitle={updateTitle}
                        title={props.survey.title}
                        default_language={props.survey.default_language}
                        languages={[props.survey.default_language]}
                    />
                    <hr />
                    <div className="survey-group">
                        <div className="survey-double-column">
                            <div className="dropdown-test">
                                <span className="double-column-label">Survey Type:</span>
                                <button className="form-control type-constraint">
                                    <span id="survey-type">{props.survey.survey_type}</span>
                                    <span id="survey-type-dropdown" className="glyphicon glyphicon-menu-down" aria-hidden="true"></span>
                                </button>
                                <div className="dropdown-content">
                                    <a value="public" onClick={changeSurveyType}>public</a>
                                    <a value="private" onClick={changeSurveyType}>private</a>
                                </div>
                            </div>
                        </div>
                        <div className="survey-double-column">
                            <div>
                                <span className="double-column-label">Default Language:</span>
                                <div>
                                    <input
                                        id="default-language"
                                        onBlur={updateDefaultLanguage}
                                        defaultValue={props.survey.default_language}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <NodeList
                    default_language={props.survey.default_language}
                    languages={[props.survey.default_language]}
                />
            </div>
            <div id="submit-button">
                <button onClick={props.submitToDatabase}>submit</button>
            </div>
        </div>
    )
}


function mapStateToProps(state){
    console.log('map state to props - survey', state.orm);

    return {
        survey: surveySelector(state)
    };
}

function mapDispatchToProps(dispatch){
    return (
        bindActionCreators({updateSurvey: updateSurvey}, dispatch)
    )
}

Survey.propTypes = {
    surveyId={props.currentSurveyId}
    submitToDatabase={submitToDatabase}
}


export default connect(mapStateToProps, mapDispatchToProps)(Survey);
