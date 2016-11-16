import React from 'react';
import NodeList from './Node.babel.js';
import SubSurvey from './SubSurvey.babel.js';

class Survey extends React.Component {

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.updateNodeList = this.updateNodeList.bind(this);
        this.back = this.back.bind(this);
        this.renderBody = this.renderBody.bind(this);
        this.submit = this.submit.bind(this);

        this.state = {
            parentSurvey: null,
            title: '',
            nodes: []
        }

    }

    updateTitle(event) {
        this.setState({title: event.target.value});
    }

    updateNodeList(nodeList) {
        console.log('nodeList', nodeList[0].node);
        this.setState({nodes: nodeList});
    }

    showSubSurvey(subSurvey) {
        this.setState({parentSurvey: subSurvey.parentNode.parentSurvey, nodes: subSurvey.nodes})
    }

    back() {
        this.setState({
            parentSurvey: this.parentNode.parentSurvey,
            nodes: this.parentNode.parentSurvey.nodes
        });

    // createSubSurvey(index, node) {
    //     console.log(index.toString());
    //     console.log('node', node);
    //     this.setState({tempNode: node});
    // }

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
        if (this.state.parentSurvey==null) {
            console.log('current', this.state.parentSurvey);
            return ( 
                <div>
                    <SurveyTitle updateTitle={this.updateTitle} />
                    <NodeList
                        parentSurvey={this.state.parentSurvey}
                        nodes={this.state.nodes}
                        showSubSurvey={this.showSubSurvey}
                        updateNodeList={this.updateNodeList}
                    />
                    <button onClick={this.submit}>submit</button>
                </div>
            );
        } else {
            return ( 
                <div>
                    {this.state.title}
                    <SubSurvey>
                    {this.parentNode.node.title}
                        <NodeList nodes={this.state.nodes}
                            updateNodeList={this.updateNodeList}
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
