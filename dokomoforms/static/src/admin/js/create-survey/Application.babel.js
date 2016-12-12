import React from 'react';
import Survey from './components/Survey.babel.js';
import cookies from '../../../common/js/cookies';
import $ from 'jquery';

class Application extends React.Component {

    constructor(props) {
        super(props);

        this.submitToDatabase = this.submitToDatabase.bind(this);
    }

    submitToDatabase(newSurvey) {
        var okay = JSON.stringify(newSurvey);
        console.log('submitting to database', okay);

        $.ajax({
            type: "POST",
            url: "/api/v0/surveys",
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify(newSurvey),
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
        return (
            <div>
                <Survey submitToDatabase={this.submitToDatabase}/>
            </div>
        );
    }
}

export default Application;