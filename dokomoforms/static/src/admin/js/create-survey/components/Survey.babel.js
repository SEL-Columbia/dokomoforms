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
            parentNode: null,
            previous: null,
            title: '',
            nodes: [{id: 4}]
        }

    }

    updateTitle(event) {
        this.setState({title: event.target.value});
    }

    updateNodeList(node, index) {
        console.log('being called')
        var nodelist = [].concat(this.state.nodes);
        console.log('should have parent survey', node.parentSurvey.nodes)
        if (index < 0) {
            console.log('less than')
            node.parentSurvey = {};
            nodelist.push(node)
        } else {
            nodelist[index] = node;
        }
        node.parentSurvey.nodes = nodelist;
        console.log('nodeList', nodelist);
        this.setState({nodes: nodelist})
        console.log('here', this.state.nodes)
    }

    showSubSurvey(node) {
        console.log('parentnode', node.subSurveys[0].parentNode)
        this.setState({previous: this.state.parentNode})
        console.log('in between', this.state)
        this.setState({parentNode: node.subSurveys[0].parentNode})
        console.log('newest state', this.state)
    }

    back() {
        console.log('back', this.state)
        this.setState({
            parentSurvey: this.state.parentNode.parentSurvey,
            nodes: this.state.parentNode.parentSurvey.nodes
        })
    }

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
        console.log('survey', this)
        var displaytitle;
        if (this.state.parentNode) displaytitle = this.state.parentNode.node;
        else displaytitle = 'first one'
        console.log('this state', this.state);
        if (this.state.parentNode==null) {
            console.log('current', this.state.parentNode);
            return ( 
                <div>
                    {displaytitle}
                    <SurveyTitle updateTitle={this.updateTitle} />
                    <NodeList
                        parentNode={this.state.parentNode}
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
                    <SubSurvey>
                        <NodeList />
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
