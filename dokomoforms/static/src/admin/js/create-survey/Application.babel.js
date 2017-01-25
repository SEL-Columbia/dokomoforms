import React from 'react';
import Survey from './components/Survey.babel.js';
import cookies from '../../../common/js/cookies';
import $ from 'jquery';
import utils from './utils.js';
import SubSurvey from './components/SubSurvey.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {addSurvey, getNode, getSurvey, denormalize} from './redux/actions.babel.js';
import {surveySelector, nodeSelector} from './redux/selectors.babel.js';

class Application extends React.Component {

    constructor(props) {
        super(props);

        this.submitToDatabase = this.submitToDatabase.bind(this);
        this.deleteExcessParams = this.deleteExcessParams.bind(this);

        this.state = {
            submitted: false,
            languages: ['English']
        }
    }

    // componentWillMount() {
    //     console.log('component will mount - applic')
    //     if (!this.props.survey) {
    //         let newSurvey = {
    //             id: utils.addId('survey'),
    //             nodes: []
    //         }
    //         this.props.addSurvey(newSurvey, 1001);
    //     }
    // }

    shouldComponentUpdate() {
        console.log('top level app update')
        if (this.state.submitted == true) return false;
        return true;
    }

    deleteExcessParams(survey, survey_id) {
        let self = this;
        let new_survey;
        new_survey = survey
        console.log('at excess params', survey, survey_id)
        delete new_survey.id;
        let newNodes = [];
        let nodeObj;
        survey.nodes.forEach(function(node_id){
            self.props.getNode(node_id)
            console.log('get', self.props.nodes)
            nodeObj = Object.assign({}, self.props.nodes[node_id])
            delete nodeObj.id
            delete nodeObj.allow_other
            if (nodeObj.node.sub_surveys) {
                delete nodeObj.node.sub_surveys
            }
            if (nodeObj.node.languages < 2) {
                delete nodeObj.node.languages
            }
            console.log(nodeObj.node.type_constraint)
            if (nodeObj.node.type_constraint=='multiple_choice') {
                console.log('its multiple choice.....')
                let newChoices = [];
                nodeObj.node.choices.forEach(function(choice){
                    delete choice.id
                    console.log('new cohce', choice)
                    newChoices.push({choice_text: choice})
                })
                nodeObj.node.choices = newChoices;
            }
            if (nodeObj.sub_surveys && nodeObj.sub_surveys.length > 0) {
                let new_subsurveys = []
                nodeObj.sub_surveys.forEach(function(survey_id) {
                    let ssObj = self.deleteExcessParams(self.props.surveys[survey_id], survey_id)
                    new_subsurveys.push(ssObj);
                })
                nodeObj.sub_surveys = new_subsurveys;
            }
            console.log(nodeObj);
            newNodes.push(nodeObj)
            console.log(newNodes)
        })
        console.log('newnodes', newNodes)
        new_survey.nodes = newNodes;
        console.log('updated survey', new_survey)
        return new_survey;
    }


    submitToDatabase() {

        var test_survey = {
          title: {
            English: 'test numbering'
          },
          default_language: 'English',
          survey_type: 'public',
          metadata: {},
          nodes: [
            {
              node: {
                number: 5,
                title: {English: 'how many people in your household?'},
                hint: {English: 'a hint'},
                type_constraint: 'integer'
              }
            }]
        }

        
        let self = this;
        this.setState({submitted: true}, function(){
            console.log('submitting')
            // console.log(self.props.surveys)
            // let database_survey = self.deleteExcessParams(self.props.surveys[1001], 1001)
            console.log('submitting this survey!!!!!', test_survey)
            // database_survey.survey_type = 'public';
            $.ajax({
                type: "POST",
                url: "/api/v0/surveys",
                contentType: 'application/json',
                processData: false,
                data: JSON.stringify(test_survey),
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

        })
    }

    render() {
        console.log(this.props.surveys, this.props.surveyView)
        console.log('surveys!!', this.props.survey)
        console.log('nodes!!!', this.props.node)
        console.log('node', this.props.node)
        let parent;
        if (this.props.surveyView && !this.props.surveyView.parent) {
            parent = this.props.surveys[this.props.surveyView.survey_id].parent;
        } else if (this.props.surveyView) {
            parent = this.props.surveyView.parent
        } else {
            parent = null
        }
        return (
            <div>
                <div>
                    <button onClick={this.props.denormalize}>click me</button>
                </div>
                {(this.props.survey) &&
                    <div>
                    <Survey
                        submitted={this.state.submitted}
                        survey={this.props.survey}
                        submitToDatabase={this.submitToDatabase}
                    />
                    </div>
                }
                {(this.props.surveys && this.props.surveyView) &&
                    <div>
                        <SubSurvey
                            previous={parent}
                            nodeId={this.props.surveyView.nodeId}
                            survey={this.props.surveys[this.props.surveyView.survey_id]}
                            languages={this.state.languages}
                        />
                    </div>
                }
            </div>
        );
    }
}

function mapStateToProps(state){
    console.log('here', 'application')
    console.log(state)
    return {
        survey: surveySelector(state),
        node: nodeSelector(state),
        currentSurveyId: state.currentSurveyId
    }
}

function matchDispatchToProps(dispatch){
    console.log('dispatch being called')
    return bindActionCreators({denormalize: denormalize, addSurvey: addSurvey, getNode: getNode, getSurvey: getSurvey}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(Application);