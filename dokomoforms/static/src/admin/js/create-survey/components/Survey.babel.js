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
            displayRoot: true,
            parentNode: null,
            title: '',
            nodes: []
        }
    }

    updateTitle(event) {
        this.setState({title: event.target.value});
    }

    updateNodeList(node, index) {
        console.log('update nodelist being called', node, index)
        var nodeList = [].concat(this.state.nodes);
        console.log('should have parent survey', node.parentSurvey.nodes)
        if (index < 0) {
            
        } nodelist.push(node)
        if (nodelist[index].id!==node.id) {
            console.log('nodes didnt match');
            return;
        }
        else {
            nodelist[index] = node;
        }
        console.log('nodeList', nodelist);
        this.setState({nodes: nodelist})
        console.log('nodes', this.state.nodes)
    }


    back(currentSubSurvey) {
        if (currentSubSurvey.parentNode==null) this.setState({displayRoot: true})
        else renderSubSurvey(currentSubSurvey.parentNode.parentSurvey)
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

    showSubSurvey() {
        this.setState({displayRoot: false})
    }

    renderSurvey() {
        console.log('root survey', this.state)
        else displaytitle = 'Define Your Survey'
        return ( 
            <div>
                {displaytitle}
                <SurveyTitle onBlur={this.updateTitle} />
                <NodeList
                    parentNode={this.state.parentNode}
                    nodes={this.state.nodes}
                    showSubSurvey={this.showSubSurvey}
                    updateNodeList={this.updateNodeList}
                />
                <button onClick={this.submit}>submit</button>
            </div>
        );
    }

    renderSubSurvey(subSurvey) {
        return (
            <div>
                <SubSurvey 
                    data={subSurvey}
                />
                <button onClick={this.back(subSurvey)}>back</button>
            </div>
        );
    }

    render() {
        if (this.state.displayRoot==true) renderSurvey()
        else renderSubSurvey()
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
