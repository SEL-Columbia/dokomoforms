import React from 'react';
import Survey from './components/Survey.babel.js';
import cookies from '../../../common/js/cookies';
import $ from 'jquery';
import utils from './utils.js';
import SubSurvey from './components/SubSurvey.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {getNode, getSurvey, denormalize} from './redux/actions.babel.js';
import {surveySelector, nodeSelector} from './redux/selectors.babel.js';

class Application extends React.Component {

    constructor(props) {
        super(props);

        this.submitToDatabase = this.submitToDatabase.bind(this);
        this.submitHandler = this.submitHandler.bind(this);

        this.state = {
            submitted: false,
            languages: ['English']
        }
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (this.state.submitted===true ||
            this.props.currentSurveyId!=nextProps.currentSurveyId) {
            console.log('top level app update');
            return true;
        }
        return false;
    }


    submitHandler(){
        this.setState({submitted: true}, function(){
            console.log('submit handler')
            this.props.denormalize();
            this.submitToDatabase();
        });
    }


    submitToDatabase() {
        let survey = this.props.survey.denormalized;
        console.log('submitting', survey)

        // this.setState({submitted: true}, function(){
        //     console.log('submitting', survey)
        //     survey.survey_type = 'public';
        //     $.ajax({
        //         type: "POST",
        //         url: "/api/v0/surveys",
        //         contentType: 'application/json',
        //         processData: false,
        //         data: JSON.stringify(denormalized),
        //         headers: {
        //           'X-XSRFToken': cookies.getCookie('_xsrf')
        //         },
        //         dataType: 'json',
        //         success: function(response) {
        //           console.log('success!!!');
        //         },
        //         error: function(response) {
        //             console.log('error')
        //           console.log(response.responseText);
        //         }
        //     })

        // })
    }

    render() {
        console.log('application current survey', this.props.currentSurveyId)
        return (
            <div>
                <div>
                    <button onClick={this.props.denormalize}>done</button>
                </div>
                <div>
                    {(this.props.currentSurveyId && this.props.currentSurveyId===1001) &&
                        <Survey
                            surveyId={this.props.currentSurveyId}
                            submitToDatabase={this.submitHandler}
                        />
                    }
                </div>
                <div>
                {(this.props.currentSurveyId && this.props.currentSurveyId!==1001) &&
                        <SubSurvey
                            surveyId={this.props.currentSurveyId}
                            languages={this.state.languages}
                        />
                }
                </div>
            </div>
        );
    }
}

function mapStateToProps(state){
    console.log('application mapstate', state)
    return {
        survey: surveySelector(state),
        currentSurveyId: state.currentSurveyId
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({denormalize: denormalize, getNode: getNode, getSurvey: getSurvey}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(Application);