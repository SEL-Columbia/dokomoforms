'use strict';

import cookies from '../../../common/js/cookies';
import $ from 'jquery';
import Survey from './components/Survey.babel.js';
import SubSurvey from './components/SubSurvey.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { orm } from './redux/models.babel.js';


class Application extends React.Component {

    constructor(props) {
        super(props);
        
        this.submitToDatabase = this.submitToDatabase.bind(this);
    }


    submitToDatabase() {
        console.log('submitting to database');

        const session = orm.session(this.props.state);

        const survey = session.Survey.withId(1001).denormalize();

        console.log('survey', survey);
        survey.survey_type = "public";

        $.ajax({
            type: "POST",
            url: "/api/v0/surveys",
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify(survey),
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
        });
    }

    render() {
        console.log('application current survey', this.props.currentSurveyId)
        return (
            <div>
                <div>
                    {(this.props.currentSurveyId && this.props.currentSurveyId===1001) &&
                        <Survey
                            surveyId={this.props.currentSurveyId}
                            submitToDatabase={this.submitToDatabase}
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
        currentSurveyId: state.currentSurveyId,
        state: state.orm,
    };
}

export default connect(mapStateToProps)(Application);
