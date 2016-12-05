import React from 'react';
import uuid from 'node-uuid';
import MultipleChoice from './MultipleChoice.babel.js';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.addOrUpdateNode = this.addOrUpdateNode.bind(this);
        
        this.state = {
            enableAddNode: false,
            nodes: []
        }
    }


    componentWillMount() {
        if (!this.props.nodes.length) {
            let nodeList = [];
            let newNode = {id: utils.addId('node')};
            newNode[this.props.default_language] = '';
            nodeList.push(newNode);
            this.setState({nodes: nodeList});
        }
    }


    listQuestions() {

        let self = this;
        let nodes = this.state.nodes;

        console.log('nodes before rendering', nodes)
        return nodes.map(function(node, index){
            return(<Node
                key={node.id} 
                index={index+1}
                data={node.node}
                enabled={self.state.enableAddNode}
                updateNode={self.updateNode.bind(null, node.id)}
                default_language={self.props.default_language}
            />)
        })
    }


    addQuestion() {
        
        let nodeList = [];
        nodeList = nodeList.concat(this.state.nodes);
        console.log('adding node', nodeList);
        let newNode = {id: utils.addId('node')};
        newNode[this.props.default_language]='';
        nodeList.push(newNode);
        this.setState({enableAddNode: false, nodes: nodeList}, function(){
            console.log('new node added', this.state.nodes);
        });
    }


    updateNode(id, node) {
        let nodeList = [];
        let updated = false;
        nodeList = nodeList.concat(this.state.nodes);
        console.log('updating choice', nodeList);

        for (var i=0; i<nodeList.length; i++) {
            if (nodeList[i].id===id) {
                console.log(nodeList[i][this.props.default_language], text)
                console.log('its updating')
                choiceList[i][this.props.default_language]=text;
                updated = true;
                break;
            }
        }

        if (updated===true) {
            this.setState({choices: choiceList}, function(){
                console.log('choice state is now updated', this.state.choices);
            })
        } else {
            console.log('something went wrong in update');
        }
    }


    render() {
        console.log('rendering nodelist', this.props.nodes)
        return (
            <div className="container">
                <div className="row">
                    <div className="col-md-9 node-list center-block">
                        {this.listQuestions()}
                        <button 
                            onClick={this.addQuestion}
                            disabled={this.state.newNode}
                        >Add Question</button>
                    </div>
                </div>
            </div>
        );
    }
}


class Node extends React.Component {

    // Node is currently referring to the full node object that contains the question
    // and the associated sub-surveys

    constructor(props) {
        super(props);

        this.getTitleOrHintValue = this.getTitleOrHintValue.bind(this);
        this.updateTitle = this.updateTitle.bind(this);
        this.updateHint = this.updateHint.bind(this);
        this.addTypeConstraint = this.addTypeConstraint.bind(this);
        // this.listChoices = this.listChoices.bind(this);
        // this.addChoice = this.addChoice.bind(this);
        // this.changeAddChoice = this.changeAddChoice.bind(this);
        this.saveNode = this.saveNode.bind(this);
        this.test = this.test.bind(this);

        this.state = {
            title: '',
            hint: '',
            type_constraint: '',
            choices: []
        }
    }

    test(){
        console.log('test');
    }


    getTitleOrHintValue(property) {
        if (!this.props.data.title) return '';
        else return this.props.data[property][this.props.default_language]
    };


    updateTitle(event) {
        let prevTitle = this.getTitleOrHintValue('title');
        // check if title input is the same as props title
        if (event.target.value===prevTitle) return;
        // check if title input is the same as current state title
        if (event.target.value===this.state.title) return;

        let titleObj = {};
        titleObj[this.props.default_language] = event.target.value;
        this.setState({title: titleObj}, function() {
            console.log('updated title', this.state.title);
            let properties = this.state.title;
            this.saveNode();
        });
    }


    updateHint(event) {
        let prevHint = this.getTitleOrHintValue('hint');
        // check if title input is the same as props title
        if (event.target.value===prevHint) return;
        // check if title input is the same as current state title
        if (event.target.value===this.state.title) return;

        let hintObj = {};
        hintObj[this.props.default_language] = event.target.value;
        this.setState({hint: hintObj}, function() {
            console.log('updated hint', this.state.hint);
            let properties = this.state.hint;
            this.saveNode();
        });
    }


    addTypeConstraint(event) {
        this.setState({type_constraint: event.target.value})
    }
    

    deleteNode() {
        if (this.props.node.saved==false) {}
    }


    saveNode() {
        let node = this.state;
        delete node['isDisabled'];
        delete node['sub_surveys'];
        if (JSON.stringify(node)===JSON.stringify(this.props.data.node)) return;

        console.log('reassigning node');
        console.log('node', node);
        console.log(this.props.data);
        let updatedNode = Object.assign(this.props.data, node);
        console.log('updatedNode', updatedNode);
        this.setState({isDisabled: false});
    }


    render() {

        let displayTitle = this.getTitleOrHintValue('title');
        let displayHint = this.getTitleOrHintValue('hint');

        return (
            <div>
                <div className="form-group row">
                    <label htmlFor="question-title" className="col-xs-2 col-form-label">Question:</label>
                </div>
                <div className="form-group row col-xs-12">
                    <textarea className="form-control question-title" rows="1" displayTitle={displayTitle}
                    onBlur={this.updateTitle}/>
                </div>
                <div className="form-group row">
                    <label htmlFor="question-type" className="col-xs-2 col-form-label">Question Type:</label>
                    <div className="col-xs-2">
                        <select className="form-control type-constraint" onChange={this.addTypeConstraint}>
                            <option value="text">text</option>
                            <option value="photo">photo</option>
                            <option value="integer">integer</option>
                            <option value="decimal">decimal</option>
                            <option value="date">date</option>
                            <option value="time">time</option>
                            <option value="timestamp">timestamp</option>
                            <option value="location">location</option>
                            <option value="facility">facility</option>
                            <option value="multiple_choice">multiple choice</option>
                            <option value="note">note</option>
                        </select>
                    </div>
                    <label htmlFor="question-hint" className="col-xs-2 col-form-label">Hint:</label>
                    <div className="form-group col-xs-6">
                        <textarea className="form-control hint-title" rows="1" displayTitle={displayHint}
                        onBlur={this.updateHint}/>
                    </div>
                </div>

                {(this.state.type_constraint==="multiple_choice") &&
                    <MultipleChoice
                        choices={this.state.choices}
                        default_language={this.props.default_language}
                    />
                }

                <button onClick={this.deleteNode}>delete</button>
                <button onClick={this.saveNode}>save</button>
            </div>
        );
    }
}


export default NodeList;
