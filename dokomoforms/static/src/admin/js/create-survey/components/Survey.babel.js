import React from 'react';
import NodeList from './NodeList.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {updateSurvey, denormalize} from './../redux/actions.babel.js';
import {surveySelector} from './../redux/selectors.babel.js';


class Survey extends React.Component {


    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.addLanguage = this.addLanguage.bind(this);
        this.updateDefaultLanguage = this.updateDefaultLanguage.bind(this);
        this.submit = this.submit.bind(this);

        this.state = {
            languages: ['English'],
            default_language: 'English',
            survey_type: 'public'
        }
    }

    shouldComponentUpdate(){
        return true;
    }

    updateTitle(language, event) {
        const titleObj = {English: event.target.value}
        this.props.updateSurvey({id: this.props.survey.id, title: titleObj})
    }
 
    updateDefaultLanguage(event) {
        this.props.updateSurvey({id: this.props.survey.id, default_language: event.target.value});
    }

    addLanguage(language){
        console.log('being called!')
        let languageList = [];
        languageList = languageList.concat(this.state.languages);
        // possible add check for duplicate
        languageList.push(language);
        this.setState({languages: languageList}, function(){
            console.log('language added', language, this.state.languages);
        });
    }

    submit() {
        // let a_survey = this.props.survey.denormalize(1001);
        // console.log('aaa', a_survey)
        this.props.submitToDatabase();
    }

    // test() {
        // var modelSurvey = {
        //   title: {English: 'languages survey 12',
        //         German: 'languages survey 12'},
        //   default_language: 'English',
        //   languages: ['English', 'German'],
        //   survey_type: 'public',
        //   metadata: {},
        //   nodes: [{
        //       node: {
        //         languages: ['English', 'German'],
        //         title: {
        //             English: 'english test',
        //             German: 'german test'
        //         },
        //         hint: {
        //             English: 'e hint',
        //             German: 'g hint'
        //         },
        //         type_constraint: 'text',
        //         logic: {}
        //     },
        //     {
        //         node: {
        //             languages: ['English', 'German'],
        //             title: {
        //                 English: 'english test 2',
        //                 German: 'german test 2'
        //             },
        //             hint: {
        //                 English: 'e hint',
        //                 German: 'g hint'
        //             },
        //             type_constraint: 'facility',
        //             logic: {}
        //         }
        //     },
        //         node: {
        //             type_constraint: 'facility',
        //             allow_multiple: true,
        //             title: {'English': 'Facility'},
        //             hint: {'English': 'Select the facility from the list, or add a new one.'},
        //             logic: {
        //                 'slat': 40.477398,
        //                 'nlat': 40.91758,
        //                 'wlng': -74.259094,
        //                 'elng': -73.700165,
        //             }
        //         }
        //     }]
    //     };
    // }


    render() {
        console.log('rendering survey')
        console.log(this.props.survey)
        return (
            <div className="container">
                {(this.props.survey) &&
                    <div>
                        <div className="col-lg-8 survey center-block">
                            <div className="survey-header header">
                                Create a Survey
                            </div>
                            <SurveyTitle 
                                updateTitle={this.updateTitle}
                                title={this.props.survey.title}
                                languages={this.state.languages}
                            />
                            <Languages 
                                languages={this.state.languages}
                                addLanguage={this.addLanguage}
                                updateDefault={this.updateDefaultLangauge}
                            />
                            <hr/>
                            <NodeList
                                default_language={this.state.default_language}
                                languages={this.state.languages}
                            />
                        </div>
                        <button onClick={this.submit}>submit</button>
                    </div>
                }
        </div>
    )
}
}


function SurveyTitle(props) {

    // const languages = props.languages;
    const languages = ['English'];

    function titleList(languages){
        return props.languages.map(function(language){
            const display = props.title ? props.title[language] : "";
            return (
                <div className="col-xs-12 survey-title" key={language}>
                    <div className="language-text"><span className="language-header">{language}</span></div>
                    <textarea id="survey-title" className="form-control survey-title-text" rows="1"
                        onBlur={props.updateTitle.bind(null, language)} placeholder={display}/>
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
    console.log('state 1', state)
    return {
        survey: surveySelector(state),
        currentSurveyId: state.currentSurveyId
    };
}

function mapDispatchToProps(dispatch){
    return (
        bindActionCreators({updateSurvey: updateSurvey, denormalize: denormalize}, dispatch)
    )
}


export default connect(mapStateToProps, mapDispatchToProps)(Survey);
