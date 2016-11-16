import React from 'react';
import uuid from 'node-uuid';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.addToNodeList = this.addToNodeList.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.listQuestions = this.listQuestions.bind(this);
        
        this.state = {
            rows: []
        }
    }

    componentWillMount() {
        if (this.props.nodes) {
            if (this.props.nodes.length < 1) {
                let newNode = {
                    id: uuid.v4(),
                    name: 'newest node',
                    saved: false
                }
                let rows = [newNode];
                this.setState({ rows })
            }
        }
    }

    listQuestions() {
        var rowsArray;

        this.state.counter++;
        if (this.state.counter > 2) return;
        
        let self = this;
        // if (this.props.nodes.length < 1 && this.state.rows.length < 1) {
        //     console.log('less than one');
        //     rowsArray = this.addQuestion()
        //     console.log('here', rowsArray)
        // } else {
        //     rowsArray = this.props.nodes;
        //     rowsArray = rowsArray.concat(this.state.rows);
        // }
        // console.log('made it');
        // console.log('lQ rows', this.state.rows)
        // return AddQuestion;

        var rowsArray = this.props.nodes.concat(this.state.rows);
        console.log(rowsArray)
        return rowsArray.map(function(node) {
                return (
                    <Node
                        key={node.id}
                        node={node}
                        addUpdateNode={self.addToNodeList}
                    />
                )
            }
        )
    }

    addQuestion() {
        console.log('props', this.props)
        var rowsArray = [];
        let newNode = {
            parentNode: this.props.parentNode,
            id: uuid.v4(),
            name: 'newest node',
            saved: false
        }
        rowsArray = rowsArray.concat(this.state.rows);
        rowsArray.push(newNode);
        this.setState({rows: rowsArray});
        console.log(this.state.rows);
    }

    addToNodeList(node) {
        let indx = -1;
        let updatedNode = node;
        console.log('node', node);
        for (var i = 0; i < this.props.nodes.length; i++) {
            if (this.props.nodes[i].id == node.id) {
                console.log('subsurvey thing', node.id, node.parentNode)
                indx = i;
                break;
            }
        }
        this.props.updateNodeList(updatedNode, indx)
        
        console.log('being called??');
        // var index = uuid.v4();
        // index = index.toString();
        // this.listQuestions(index);
    }

    render() {
        console.log('here??', this.props)
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
        let node = this.props.node;
        let ss = [];
        ss.push(newSubSurvey)
        node.subSurveys = ss
        console.log('state subsurveys', ss)
        console.log(this.props.node.id)
        this.props.addUpdateNode(node);
        this.props.showSubSurvey(newSubSurvey);
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