import React from 'react';
import NodeList from './Node.babel.js';
import cookies from '../../../../common/js/cookies';

class Survey extends React.Component {

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.addDefaultLanguage = this.addDefaultLanguage.bind(this);
        this.updateNodeList = this.updateNodeList.bind(this);
        this.submit = this.submit.bind(this);
        this.test = this.test.bind(this);

        this.state = {
            title: {},
            hint: {},
            default_language: 'English',
            survey_type: '',
            nodes: []
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

    addDefaultLanguage(event) {
        this.setState({default_language: event.target.value}, function(){
            console.log('set state: default language updated');
        });
    }

    updateNodeList(nodelist) {
        console.log('update nodelist being called')
        console.log('this state nodes', this.state.nodes)
        // let nodelist = [];
        // nodelist = nodelist.concat(this.state.nodes);
        // node.saved = true;
        // console.log('nodelist before', nodelist)
        // if (index < 0) nodelist.push(node)
        // else nodelist[index] = node;
        // console.log('nodeList', nodelist);
        this.setState({nodes: nodelist}, function(){
            console.log('nodes from survey', this.state.nodes);
        })
    }

    submit() {
        console.log('being called?')
        const newSurvey = {
            title: this.state.title,
            default_language: this.default_language,
            nodes: this.state.nodes
        }
        console.log('before submitting', newSurvey);
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
            <div>
                <SurveyTitle updateTitle={this.updateTitle}/>
                <NodeList
                    nodes={this.state.nodes}
                    default_language={this.state.default_language}
                    updateNodeList={this.updateNodeList}
                    language={this.state.default_language}
                />
            </div>
        );
    }
}


class SurveyTitle extends React.Component {

    render() {
        return (
            <div>
                Survey Title: <input type="text" onBlur={this.props.updateTitle} />
            </div>
        );
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


class temp extends React.Component {
    render() {
        return (
            <div>
                <div className="col-md-12">
                    {displaytitle}
                    <SurveyTitle updateTitle={this.updateTitle} />
                    <DefaultLanguage addDefaultLanguage={this.addDefaultLanguage} />
                </div>
            </div>
        )
    }
}


export default Survey;
