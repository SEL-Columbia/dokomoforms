import React from 'react';
import NodeList from './Node.babel.js';
import SubSurvey from './SubSurvey.babel.js';

class Survey extends React.Component {

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.updateNodeList = this.updateNodeList.bind(this);
        this.createSubSurvey = this.createSubSurvey.bind(this);
        this.back = this.back.bind(this);
        this.renderBody = this.renderBody.bind(this);
        this.submit = this.submit.bind(this);

        this.state = {
            title: '',
            nodes: [],
            surveyIDs: ['first'],
            current: 0,
            tempNode: ''
        }

    }

    updateTitle(event) {
        this.setState({title: event.target.value});
    }

    updateNodeList(nodeList) {
        console.log('nodeList', nodeList[0].node);
        this.setState({nodes: nodeList});
    }

    createSubSurvey(index, node) {
        console.log(index.toString());
        console.log('node', node);
        this.setState({tempNode: node});
        var surveyArr = this.state.surveyIDs;
        surveyArr.push(index.toString());
        this.setState({surveyIDs: surveyArr});
        this.setState({current: ++this.state.current})
    }

    back() {
        this.setState({current: --this.state.current});
    }

    submit() {
        console.log('being called???')
        const newSurvey = {
            title: this.state.title,
            nodes: this.state.nodes
        }
        console.log('before submitting', newSurvey.nodes[0]);
        this.props.submitToDatabase(newSurvey);
    }

    renderBody() {
        console.log('this state', this.state);
        console.log('current', this.state.current);
        var currentIndex = this.state.surveyIDs[this.state.current];
        if (currentIndex=='first') {
            return ( 
                <div>
                    <SurveyTitle updateTitle={this.updateTitle} />
                    <NodeList key={currentIndex}
                        updateNodeList={this.updateNodeList}
                        handleSubSurvey={this.createSubSurvey}
                    />
                    <button onClick={this.submit}>submit</button>
                </div>
            );
        } else {
            return ( 
                <div>
                    {this.state.title}
                    <SubSurvey key={currentIndex}>
                    {currentIndex}
                    {this.state.tempNode}
                        <NodeList key={currentIndex}
                            updateNodeList={this.updateNodeList}
                            handleSubSurvey={this.createSubSurvey}
                        />
                    </SubSurvey>
                    <button onClick={this.back}>back</button>
                </div>
            );
        }
    }

    render() {
        return (
            <div>
                {this.renderBody()}
            </div>
        );
    }

}

class SurveyTitle extends React.Component {

    render() {
        return (
            <div>
                <input type="text" onChange={this.props.updateTitle} />
            </div>
        );
    }
}

export default Survey;
