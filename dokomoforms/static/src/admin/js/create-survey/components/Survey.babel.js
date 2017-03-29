import React from 'react';
import NodeList from './NodeList.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { updateSurvey } from './../redux/actions.babel.js';
import { surveySelector } from './../redux/selectors.babel.js';
import { orm } from './../redux/models.babel.js';


function Survey(props) {

    // constructor(props) {
    //     super(props);

    //     this.updateTitle = this.updateTitle.bind(this);
    //     this.addLanguage = this.addLanguage.bind(this);
    //     this.updateDefaultLanguage = this.updateDefaultLanguage.bind(this);

    //     this.state = {
    //         languages: ['English'],
    //         default_language: 'English',
    //         survey_type: 'public',
    //     }
    // }

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

    function addLanguage(language){
        let languageList = [];
        languageList = languageList.concat(this.state.languages);
        // possible add check for duplicate
        languageList.push(language);
        // this.setState({languages: languageList}, function(){
        //     console.log('language added', language, this.state.languages);
        // });
    }



    console.log('the updated survey', props.survey)
    return (
        <div className="container survey col-lg-7">
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
                                    <span style={{float: "left"}}>{props.survey.survey_type}</span>
                                    <span className="glyphicon glyphicon-menu-down" aria-hidden="true" style={{float: "right"}}></span>
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
                                    <input onBlur={updateDefaultLanguage} defaultValue={props.survey.default_language}/>
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
            <div style={{textAlign: "center", margin: "15px", fontSize: "23px"}}>
                <button onClick={props.submitToDatabase}>submit</button>
            </div>
        </div>
    )
}


function SurveyTitle(props) {

    const languages = [props.default_language]

    console.log('languages', languages)

    function titleList(languages){
        return props.languages.map(function(language){
            const display = props.title ? props.title[language] : "";
            return (
                <div className="col-xs-12 survey-title" key={language}>
                    <div className="language-text"><span className="language-header">{language}</span></div>
                    <textarea id="survey-title" className="form-control survey-title-text" rows="1"
                        onBlur={props.updateTitle.bind(null, language)} defaultValue={display}/>
                </div>
            )
        })
    }

        return (
            <div>
                <div className="form-group row survey-group">
                    <label htmlFor="survey-title" className="col-xs-4 col-form-label survey-label">Survey Title: </label>
                    {titleList()}
                </div>
            </div>
        )
}


function Languages(props){

    const languages = props.languages;

    function languageList(languages){
        return props.languages.map(function(language){
            console.log('language???', language)
            return (
                <option key={language} value={language}>{language}</option>
            )
        })
    }

    function languageHandler(event) {
        if (!event.target.value.length) return;
        console.log('handling', event.target.value)
        const newLang = event.target.value;
        event.target.value = '';
        props.addLanguage(newLang);
    }

    return (
        <div>
            <div className="form-group row survey-group">
                <label htmlFor="survey-title" className="col-xs-4 col-form-label survey-label">Languages: </label>
                <div className="col-xs-12">
                    <div>
                        Add Language: <input type="text" onBlur={languageHandler}/>
                    </div>
                    <div>
                        Default Language:
                        <select onChange={props.updateDefault}>
                            {languageList()}
                        </select>
                    </div>
                </div>
            </div>
        </div>
    )
}


function mapStateToProps(state){
    console.log('state survey', state.orm);

    return {
        survey: surveySelector(state)
    };
}

function mapDispatchToProps(dispatch){
    return (
        bindActionCreators({updateSurvey: updateSurvey}, dispatch)
    )
}


export default connect(mapStateToProps, mapDispatchToProps)(Survey);
