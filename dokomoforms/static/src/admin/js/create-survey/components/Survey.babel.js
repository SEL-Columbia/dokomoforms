import React from 'react';
import NodeList from './NodeList.babel.js';
import cookies from '../../../../common/js/cookies';
import {connect} from 'react-redux';


class Survey extends React.Component {


    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.addLanguage = this.addLanguage.bind(this);
        this.updateDefault = this.updateDefault.bind(this);
        this.updateNodeList = this.updateNodeList.bind(this);
        this.submit = this.submit.bind(this);

        this.state = {
            title: {},
            languages: ['English'],
            default_language: 'English',
            survey_type: 'public',
            nodes: [],
            isSubmitted: false
        }
    }


    updateTitle(language, event) {
        let newTitle = {};
        newTitle[language] = event.target.value;
        
        let titleObj = Object.assign({}, this.state.title, newTitle);
        this.setState({title: titleObj}, function() {
            console.log('updated title', this.state.title);
        })
    }

    updateDefault(event) {
        this.setState({default_language: event.target.value}, function(){
            console.log('set state: default language updated', this.state.default_language);
        });
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

    updateNodeList(nodelist) {
        console.log('update nodelist being called')
        console.log('this state nodes', this.state.nodes)
        // let nodes = [];
        // nodes = nodelist.concat(this.state.nodes);
        // node.saved = true;
        // console.log('nodelist before', nodelist)
        // if (index < 0) nodelist.push(node)
        // else nodelist[index] = node;
        console.log('nodeList', nodelist);
        this.setState({nodes: nodelist}, function(){
            console.log('nodes from survey', this.state.nodes);
        })
    }

    submit() {
        // var survey2 = {
        //     title: {English: 'other responses'},
        //     default_language: 'English',
        //       survey_type: 'public',
        //       metadata: {},
        //       nodes: [{
        //         node: {
        //             type_constraint: 'integer',
        //             allow_multiple: true,
        //             allow_other: true,
        //             title: {'English': 'multiple responses'},
        //             hint: {'English': 'select more than one'}
        //         }
        //     }]
        // }
        // console.log(survey2)
        // this.props.submitToDatabase(survey2)
        console.log('being called?')
        this.setState({isSubmitted: true}, function(){
            const newSurvey = {
                title: this.state.title,
                languages: this.state.languages,
                default_language: this.state.default_language,
                survey_type: this.state.survey_type,
                nodes: this.state.nodes
            }
            console.log('before submitting', newSurvey);
            this.props.submitToDatabase(newSurvey);
        })
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



        // var modelNode = {
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
        // }


    render() {
        return (
            <div className="container">
                <div className="col-lg-8 survey center-block">
                    <div className="survey-header header">
                        Create a Survey
                    </div>
                    <SurveyTitle 
                        updateTitle={this.updateTitle}
                        languages={this.state.languages}
                    />
                    <hr/>
                    <Languages 
                        languages={this.state.languages}
                        addLanguage={this.addLanguage}
                        updateDefault={this.updateDefault}
                    />
                    <NodeList
                        submitting={this.state.isSubmitted}
                        nodes={this.state.nodes}
                        default_language={this.state.default_language}
                        updateNodeList={this.updateNodeList}
                        languages={this.state.languages}
                    />
                    <button onClick={this.update_default}>default</button>
                </div>
                <button onClick={this.submit}>submit</button>
            </div>
        );
    }
}


function SurveyTitle(props) {

    const languages = props.languages;

    function titleList(languages){
        return props.languages.map(function(language){
            return (
                <div className="col-xs-12 survey-title" key={language}>
                    <div className="language-text"><span className="language-header">{language}</span></div>
                    <textarea id="survey-title" className="form-control survey-title-text" rows="1"
                        onBlur={props.updateTitle.bind(null, language)}/>
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
                    Add Language: <input type="text" onBlur={languageHandler}/>
                    Default Language:
                        <select onChange={props.updateDefault}>
                            {languageList()}
                        </select>
                </div>
            </div>
        </div>
    )
}

function mapStateToProps(state){
    return {
        surveys: state.surveys
    };
}

export default connect(mapStateToProps)(Survey);

// export default Survey;
