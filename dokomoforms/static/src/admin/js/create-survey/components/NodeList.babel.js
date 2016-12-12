import React from 'react';
import utils from './../utils.js';
import Node from './Node.babel.js';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.deleteQuestion = this.deleteQuestion.bind(this);
        this.updateNode = this.updateNode.bind(this);
        
        this.state = {
            enableAddNode: false,
            nodes: [{id: utils.addId('node'), node: {}}]
        }
    }


    componentWillMount() {
        // if (!this.props.nodes.length) {
        //     let nodeList = [];
        //     let newNode = {
        //         id: utils.addId('node'),
        //         node: {}
        //     };
        //     nodeList.push(newNode);
        //     this.setState({nodes: nodeList});
        // }
    }

    componentWillReceiveProps(nextProps) {
        if (this.props.submitting===true) return;
        if (nextProps.submitting===true) {
            console.log('nodelist seeing saved')
            return this.props.updateNodeList(this.state.nodes);
        }
    }


    shouldComponentUpdate(nextProps, nextState) {
        console.log('being called!');
        if (this.props.default_language!==nextProps.default_language) {
            console.log('default language changed');
            console.log(this.props.default_language, nextProps.default_language)
            return true;
        }
        if (this.state!==nextState) {
            console.log('state change in nodelist');
            return true;
        }
        if (this.props.languages.length!==nextProps.languages.length) {
            console.log('question added or deleted');
            return true;
        }
        return false;
    }


    listQuestions() {

        let self = this;
        let nodes = this.state.nodes;

        console.log('nodes before rendering', nodes)
        return nodes.map(function(node, index){
            return(
                <Node
                    saved={self.props.submitting}
                    key={node.id} 
                    index={index+1}
                    data={node.node}
                    enabled={self.state.enableAddNode}
                    updateNode={self.updateNode.bind(null, node.id)}
                    deleteQuestion={self.deleteQuestion.bind(null, index)}
                    default_language={self.props.default_language}
                    languages={self.props.languages}
                />
            )
        })
    }


    addQuestion() {
        let nodeList = [];
        nodeList = nodeList.concat(this.state.nodes);
        console.log('adding node', nodeList);
        let newNode = {id: utils.addId('node'), node: {}};
        nodeList.push(newNode);
        this.setState({enableAddNode: false, nodes: nodeList}, function(){
            console.log('new node added', this.state.nodes);
        });
    }

    deleteQuestion(index) {
        let nodeList = [];
        nodeList = nodeList.concat(this.state.nodes);
        nodeList.splice(index, 1);
        this.setState({nodes: nodeList}, function(){
            console.log('node deleted', this.state.nodes);
        })
    }


    updateNode(id, node) {

        let nodeList = [];
        let updated = false;
        nodeList = nodeList.concat(this.state.nodes);
        console.log('updating node', nodeList);

        for (var i=0; i<nodeList.length; i++) {
            if (nodeList[i].id===id) {
                console.log(id, node);
                console.log('its updating', nodeList)
                nodeList[i].node = node;
                updated = true;
                break;
            }
        }
        if (updated===true) {
            this.setState({nodes: nodeList}, function(){
                console.log('node state is now updated', this.state.nodes);
                // this.props.updateNodeList(this.state.nodes);
            })
        } else {
            console.log('something went wrong in update');
        }
    }


    render() {
        console.log('rendering nodelist', this.props.nodes)
        return (
            <div className="node-list">
                <div className="header">
                    Questions
                </div>
                {this.listQuestions()}
                <button 
                    onClick={this.addQuestion}
                >Add Question</button>
            </div>
        );
    }
}

export default NodeList
