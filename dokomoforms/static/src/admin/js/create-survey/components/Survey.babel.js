import React from 'react';
import NodeList from './Node.babel.js';
import SubSurvey from './SubSurvey.babel.js';

class Survey extends React.Component {

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.updateNodeList = this.updateNodeList.bind(this);
        this.back = this.back.bind(this);
        this.submit = this.submit.bind(this);
        this.showSubSurvey = this.showSubSurvey.bind(this);
        this.renderSurvey = this.renderSurvey.bind(this);
        this.renderSubSurvey = this.renderSubSurvey.bind(this);

        this.state = {
            displaySurvey: 'root',
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
        console.log('this state nodes', this.state.nodes)
        let nodelist = [];
        nodelist = nodelist.concat(this.state.nodes);
        node.saved = true;
        console.log('nodelist before', nodelist)
        if (index < 0) nodelist.push(node)
        else nodelist[index] = node;
        console.log('nodeList', nodelist);
        this.setState({nodes: nodelist})
    }


    back(currentSubSurvey) {
        if (currentSubSurvey.parentNode==null) this.setState({displaySurvey: 'root'})
        else renderSubSurvey(currentSubSurvey.parentNode.parentSurvey)
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

    showSubSurvey(subSurvey) {
        this.setState({displaySurvey: subSurvey, parentNode: subSurvey.parentNode});
    }

    updateSurvey(subSurvey) {
        this.setState({displaySurvey: subSurvey});
    }

    renderSurvey() {
        console.log('root survey', this.state)
        let displaytitle = 'Define Your Survey'
        return ( 
            <div>
                {displaytitle}
                <SurveyTitle onBlur={this.updateTitle} />
                <NodeList
                    parentSurvey={this.state.parentSurvey}
                    nodes={this.state.nodes}
                    showSubSurvey={this.showSubSurvey}
                    updateNodeList={this.updateNodeList}
                />
                <button onClick={this.submit}>submit</button>
            </div>
        );
    }

    renderSubSurvey() {
        return (
            <div>
                <SubSurvey 
                    data={this.state.displaySurvey}

                />
                <button onClick={this.back(subSurvey)}>back</button>
            </div>
        );
    }

    render() {
        if (this.state.displaySurvey=='root') return this.renderSurvey()
        else return this.renderSubSurvey()
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
