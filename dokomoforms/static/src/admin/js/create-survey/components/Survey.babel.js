import React from 'react';
import NodeList from './components/Node.babel.js';

class Survey extends React.Component {

    constructor(props) {
        super(props);

        this.updateQuestion = this.updateQuestion.bind(this);
        this.updateNodes = this.updateNodes.bind(this);
        this.saveSurvey = this.saveSurvey.bind(this);

        this.state = {
            title: '',
            nodes: []
        };
    }

    updateQuestion(event) {
        // this.setState({title: event.target.value});
    }

    updateNodes(nodeList) {
        this.setState({nodes: nodeList});
    }

    saveSurvey() {
        const survey = this.state;
        console.log('from survey', survey);
        this.props.buildSurvey(survey);
    }

    render() {

        return (
            <div>
                <SurveyTitle updateQuestion={this.updateQuestion}>
                {this.state.title}</SurveyTitle>
                <NodeList updateNodes={this.updateNodes}/>
                <button onClick={this.saveSurvey}>save survey</button>
            </div>
        );
    }
}

class SurveyTitle extends React.Component {

    render() {
        return (
            <div>
                <input type="text" onChange={this.props.updateQuestion} />
            </div>
        );
    }
}

export default Survey;
