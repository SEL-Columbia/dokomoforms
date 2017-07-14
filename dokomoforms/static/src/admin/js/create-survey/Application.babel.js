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


        var oisu = {
          title: {
            English: 'int bucket test'
          },
          default_language: 'English',
          survey_type: 'public',
          nodes: [
            {
              node: {
                title: {English: 'the bucket is [5)'},
                hint: {English: 'a hint'},
                type_constraint: 'integer',
              },
              sub_surveys: [
                    {
                        buckets: [
                            {
                                bucket_type: 'integer',
                                bucket: '[2, 5]'
                            }
                        ],
                        nodes: [
                            {
                                node: {
                                    title: {English: 'you picked over five - give integer answer'},
                                    type_constraint: 'integer'
                                }
                            }
                        ]
                    },
              ]
            }]
        }

        $.ajax({
            type: "POST",
            url: "/api/v0/surveys",
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify(oisu),
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
        state: state.orm
    };
}

Application.propTypes = {
    currentSurveyId: React.PropTypes.number,
    state: React.PropTypes.object
};

export default connect(mapStateToProps)(Application);
