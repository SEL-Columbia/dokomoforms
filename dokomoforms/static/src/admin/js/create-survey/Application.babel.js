import React from 'react';
import Survey from './components/Survey.babel.js';

class Application extends React.Component {

    constructor(props) {
        super(props);

        this.submitToDatabase = this.submitToDatabase.bind(this);
    }

    submitToDatabase(newSurvey) {
        var okay = JSON.stringify(newSurvey);
        console.log('submitting to database', okay);
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