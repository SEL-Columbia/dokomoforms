import React from 'react';
import uuid from 'node-uuid';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.addToNodeList = this.addToNodeList.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.listQuestions = this.listQuestions.bind(this);
        
    }

    listQuestions() {
        let rowsArray = this.props.nodes;
        rowsArray.map(function(node) {
            return (
                    <Node
                        key={node.id}
                        node={node}
                        addUpdateNode={this.addToNodeList}
                    />
                )
            }
        )
    }

    addQuestion() {
        let newNode = {
            id: uuid.v4(),
            saved: false
        }
        let rowsArray = this.state.rows;
        rowsArray.push(newNode);
        this.setState({rows: rowsArray});
    }

    addToNodeList(id) {
        console.log('hello')
    }


    render() {
        return (
            <div>
                {this.listQuestions()}
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
            subSurveys: []
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
        let newSubSurvey = {
            parentNode: this.props.node,
            nodes: []
        }
        this.subSurveys.push(newSubSurvey)
    }

    saveNode() {
        this.setState({isDisabled: false})
    }

    render() {
        return (
            <div>
                Question: <input type="text" placeholder={this.props.title}
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