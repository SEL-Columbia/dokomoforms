import React from 'react';
import uuid from 'node-uuid';

console.log(uuid);

class NodeList extends React.Component {

    constructor(props) {
        super(props);

        this.addToNodeList = this.addToNodeList.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.listQuestions = this.listQuestions.bind(this);
        
        this.state = {
            questions: 1,
            nodes: []
        };
    }

    addToNodeList(newNode) {
        const nodeArr = this.state.nodes;
        nodeArr.push(newNode);
        this.setState({nodes: nodeArr}, function(){
            console.log('added to list!', newNode, this.state.nodes)
            this.props.updateNodeList(this.state.nodes);
        })
    }

    addQuestion() {
        let currentQuestions = this.state.questions;
        currentQuestions++;
        this.setState({questions: currentQuestions});
    }

    listQuestions(num) {
        var rows = [];
        for (var i=0; i<num; i++) {
            console.log(this.props.handleSubSurvey);
            rows.push(
                    <Node
                        index={i}
                        addToList={this.addToNodeList}
                        I={this.props.handleSubSurvey}
                    />);
        }
        return rows;
    }

    render() {
        return (
            <div>
                {this.listQuestions(this.state.questions)}
                <button onClick={this.addQuestion}>Add Question</button>
            </div>
        );
    }
}

class Node extends React.Component {

    // Node is currently referring to the full node object that contains the question
    // and the associated sub-surveys

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.addSubsurvey = this.addSubSurvey.bind(this);
        this.saveNode = this.saveNode.bind(this);

        this.state = {
            isDisabled: true,
            title: '',
            sub_surveys: []
        }
    }

    updateTitle(event) {
        this.setState({title: event.target.value});
    }

    deleteNode() {
        /// languages???
        const message ='Are you sure you want to delete this question and all of it\'s sub-surveys?'

        if(confirm(message)) {
            console.log('deleted!');
        } else {
            console.log('nevermind!!');
        }
    }

    addSubSurvey() {
        console.log(uuid);
        var index = uuid.v4();
        this.props.I(index, this.state.title);
    }

    saveNode() {
        var node = { 
            node: {}
        };
        node.node.title = this.state.title;
        if (this.state.sub_surveys.length) {
            node.sub_surveys = this.state.sub_surveys;
        }
        this.props.addToList(node);
        this.setState({isDisabled: false})
    }

    render() {
        return (
            <div>
                Question: <input type="text"
                    onChange={this.updateTitle}/>
                    <button onClick={this.deleteNode}>delete</button>
                    <button onClick={this.saveNode}>save</button>
                    <button 
                        disabled={this.state.isDisabled}
                        onClick={this.addSubsurvey}
                    >add sub-survey</button>
            </div>
        );
    }
}

export default NodeList;