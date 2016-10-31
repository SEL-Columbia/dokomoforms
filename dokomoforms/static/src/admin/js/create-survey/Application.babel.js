import React from 'react';
import Survey from './components/Survey.babel.js';

class Application extends React.Component {

    constructor(props) {
        super(props);

        this.submit = this.submit.bind(this);
        this.buildSurvey = this.buildSurvey.bind(this);

        // newSurvey starts out empty. It's getting built
        // in the child components
        this.state = {
            newSurvey: {}
        };
    }

    buildSurvey(survey) {
        console.log('from application', survey);
        this.setState({newSurvey: survey});
    }

    submit() {
        console.log('submitting to database', this.state.newSurvey);
    }

    render() {
        const buildSurvey = this.buildSurvey;
        return (
            <div>
                <Survey buildSurvey={buildSurvey} />
                <button onClick={this.submit}>Submit</button>
            </div>
        );
    }
}

export default Application;