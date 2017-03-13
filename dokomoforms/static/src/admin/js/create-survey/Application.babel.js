'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import cookies from '../../../common/js/cookies';
import $ from 'jquery';
import Survey from './components/Survey.babel.js';
import SubSurvey from './components/SubSurvey.babel.js';
import { connect } from 'react-redux';
import { orm } from './redux/models.babel.js';


function Application(props) {

    function submitToDatabase() {

        const session = orm.session(props.state);

        const survey = session.Survey.withId(1001).denormalize();

        console.log('submitting to database', survey);

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
    
    return (
        <div>
            <div>
                {(props.currentSurveyId && props.currentSurveyId===1001) &&
                    <Survey
                        surveyId={props.currentSurveyId}
                        submitToDatabase={submitToDatabase}
                    />
                }
            </div>
            <div>
                {(props.currentSurveyId && props.currentSurveyId!==1001) &&
                    <SubSurvey
                        surveyId={props.currentSurveyId}
                        languages={['English']}
                    />
                }
            </div>
        </div>
    );
}

function mapStateToProps(state){
    console.log('application mapstate', state);
    return {
        currentSurveyId: state.currentSurveyId,
        state: state.orm,
    };
}

Application.propTypes = {
    currentSurveyId: React.PropTypes.number,
    state: React.PropTypes.object
};

export default connect(mapStateToProps)(Application);
