import React from 'react';
import uuid from 'node-uuid';
import utils from './../utils.js';
import MultipleChoice from './MultipleChoice.babel.js';
import { FacilityLogic, MinMaxLogic } from './Bucket.babel.js';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.updateNode = this.updateNode.bind(this);
        
        this.state = {
            enableAddNode: false,
            nodes: []
        }
    }


    componentWillMount() {
        if (!this.props.nodes.length) {
            let nodeList = [];
            let newNode = {
                id: utils.addId('node'),
                node: {}
            };
            nodeList.push(newNode);
            this.setState({nodes: nodeList});
        }
    }


    listQuestions() {

        let self = this;
        let nodes = this.state.nodes;

        console.log('nodes before rendering', nodes)
        return nodes.map(function(node, index){
            return(
                <Node
                    key={node.id} 
                    index={index+1}
                    data={node.node}
                    enabled={self.state.enableAddNode}
                    updateNode={self.updateNode.bind(null, node.id)}
                    default_language={self.props.default_language}
                />
            )
        })
    }


    addQuestion() {
        let nodeList = [];
        nodeList = nodeList.concat(this.state.nodes);
        console.log('adding node', nodeList);
        let newNode = {id: utils.addId('node')};
        newNode.node[this.props.default_language]='';
        nodeList.push(newNode);
        this.setState({enableAddNode: false, nodes: nodeList}, function(){
            console.log('new node added', this.state.nodes);
        });
    }


    updateNode(id, node) {

        let nodeList = [];
        let updated = false;
        nodeList = nodeList.concat(this.state.nodes);
        console.log('updating node', nodeList);

        for (var i=0; i<nodeList.length; i++) {
            if (nodeList[i].id===id) {
                console.log('its updating')
                nodeList[i].node = node;
                updated = true;
                break;
            }
        }
        if (updated===true) {
            this.setState({nodes: nodeList}, function(){
                console.log('node state is now updated', this.state.nodes);
                this.props.updateNodeList(this.state.nodes);
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
        this.saveNode = this.saveNode.bind(this);

        this.state = {
            title: '',
            hint: '',
            type_constraint: '',
            choices: [],
            saved: false
        }
    }


    getTitleOrHintValue(property) {
        if (!this.props.data ||
            !this.props.data[property]) return '';
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
        console.log('node after state', node)
        if (!node.choices.length) delete node.choices;
        if (JSON.stringify(node)===JSON.stringify(this.props.data.node)) return;

        console.log('reassigning node');
        console.log('node', node);
        console.log(this.props.data);
        let updatedNode = Object.assign(this.props.data, node);
        console.log('updatedNode', updatedNode);
        this.props.updateNode(updatedNode);
    }

    saveNode(){
        this.setState({saved: true}, function(){
            this.updateNode()
        })
    }


    render() {

        let displayTitle = this.getTitleOrHintValue('title');
        let displayHint = this.getTitleOrHintValue('hint');

        return (
            <div className="node">
                <div className="form-group row">
                    <label htmlFor="question-title" className="col-xs-2 col-form-label">Question:</label>
                </div>
                <div className="form-group row col-xs-12">
                    <textarea className="form-control question-title" rows="1" displayTitle={displayTitle}
                    onBlur={this.updateTitle}/>
                </div>
                <div className="form-group row">
                    <TypeConstraint addTypeConstraint={this.addTypeConstraint} />
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

                {(this.state.type_constraint==="facility") &&
                    <FacilityLogic />
                }

                {(this.state.type_constraint==="decimal") &&
                    <MinMaxLogic />
                }

                <button onClick={this.deleteNode}>delete</button>
                <button onClick={this.saveNode}>save</button>
            </div>
        );
    }
}

class TypeConstraint extends React.Component {
    render(){
        return(
            <div>
                <label htmlFor="question-type" className="col-xs-2 col-form-label">Question Type:</label>
                <div className="col-xs-2">
                    <select className="form-control type-constraint" onChange={this.props.addTypeConstraint}>
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
            </div>
        );
    }
}


export default NodeList;
