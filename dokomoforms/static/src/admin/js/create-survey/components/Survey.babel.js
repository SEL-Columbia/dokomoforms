import React from 'react';
import NodeList from './NodeList.babel.js';
import cookies from '../../../../common/js/cookies';


class Survey extends React.Component {


    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.updateDefault = this.updateDefault.bind(this);
        this.addLanguage = this.addLanguage.bind(this);
        this.updateNodeList = this.updateNodeList.bind(this);
        this.submit = this.submit.bind(this);
        this.test = this.test.bind(this);

        this.state = {
            title: {},
            languages: ['English'],
            default_language: 'English',
            survey_type: 'public',
            nodes: [],
            isSubmitted: false
        }
    }


    updateTitle(event) {
        if (this.state.title[this.state.default_language]===event.target.value) return;
        let titleObj = {};
        titleObj[this.state.default_language] = event.target.value;
        this.setState({title: titleObj}, function(){
            console.log('set state: title updated');
        });
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
        console.log('being called?')
        this.setState({isSubmitted: true}, function(){
            const newSurvey = {
                title: this.state.title,
                default_language: this.state.default_language,
                survey_type: this.state.survey_type,
                nodes: this.state.nodes
            }
            delete newSurvey.nodes[0].id;
            console.log('before submitting', newSurvey);
            this.props.submitToDatabase(newSurvey);
        })
    }

    test() {
        var modelSurvey = {
          title: {English: 'languages survey 12',
                German: 'languages survey 12'},
          default_language: 'English',
          languages: ['English', 'German'],
          survey_type: 'public',
          metadata: {},
          nodes: [{
              node: {
                languages: ['English', 'German'],
                title: {
                    English: 'english test',
                    German: 'german test'
                },
                hint: {
                    English: 'e hint',
                    German: 'g hint'
                },
                type_constraint: 'text',
                logic: {}
            }
            },
            {
                node: {
                    languages: ['English', 'German'],
                    title: {
                        English: 'english test 2',
                        German: 'german test 2'
                    },
                    hint: {
                        English: 'e hint',
                        German: 'g hint'
                    },
                    type_constraint: 'facility',
                    logic: {}
                }
            }]
        };

        var survey2 = {
            title: {English: 'facility survey test'},
            default_language: 'English',
              survey_type: 'public',
              metadata: {},
              nodes: [{
                  node: {
                    type_constraint: 'facility',
                    title: {'English': 'Facility'},
                    hint: {'English': 'Select the facility from the list, or add a new one.'},
                    logic: {
                        'slat': 40.477398,
                        'nlat': 40.91758,
                        'wlng': -74.259094,
                        'elng': -73.700165,
                    }
                }
            }]
        }


        var modelNode = {
                languages: ['English', 'German'],
                title: {
                    English: 'english test',
                    German: 'german test'
                },
                hint: {
                    English: 'e hint',
                    German: 'g hint'
                },
                type_constraint: 'text',
                logic: {}
        }

        $.ajax({
            type: "POST",
            url: "/api/v0/surveys",
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify(survey2),
            headers: {
              'X-XSRFToken': cookies.getCookie('_xsrf')
            },
            dataType: 'json',
            success: function(response) {
              console.log('success!!!');
            },
            error: function(response) {
                console.log('error')
              console.log(response.responseText);
            }
        })
    }


    render() {
        let displaytitle = 'Define Your Survey';
        return (
            <div className="container">
                <div className="col-lg-8 survey center-block">
                    <div className="survey-header header">
                        Create a Survey
                    </div>
                    <SurveyTitle updateTitle={this.updateTitle}/>
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
                    <button onClick={this.submit}>submit</button>
                </div>
            </div>
        );
    }
}


class SurveyTitle extends React.Component {

    render() {
        return (
            <div>
                <div className="form-group row survey-group">
                    <label htmlFor="survey-title" className="col-xs-4 col-form-label survey-label">Survey Title: </label>
                <div className="col-xs-12">
                    <textarea className="form-control survey-title" rows="1"
                        onBlur={this.props.updateTitle}/>
                </div>
                </div>
            </div>
        )
    }
}


class DefaultLanguage extends React.Component {

    render() {
        return (
            <div>
                Default Language: <input type="text" onBlur={this.props.updateDefault} />
            </div>
        );
    }
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



export default Survey;
