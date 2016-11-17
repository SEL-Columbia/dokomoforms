import React from 'react';
import uuid from 'node-uuid';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.addToNodeList = this.addToNodeList.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.listQuestions = this.listQuestions.bind(this);
        
        this.state = {
            newNode: undefined
        }
    }

    componentWillMount() {
        if (this.props.nodes && this.props.nodes.length < 1) {
                let newNode = {
                    id: uuid.v4(),
                    parentNode: this.props.parentNode,
                    saved: false,
                    node: {
                        title: {"English": ""}
                    }
                };
                this.setState({newNode})
            }
        }
    }

    listQuestions() {
        let rows;

        this.state.counter++;
        if (this.state.counter > 2) return;
        
        const self = this;
        let rows = this.props.nodes;
        if (this.state.newNode) rows.push(newNode); 
        console.log(rows)
        return rows.map(function(node, i) {
            console.log('saved?', node.saved)
            return (
                <Node
                    key={node.id}
                    index={i}
                    node={node}
                    addOrUpdateNode={self.addOrUpdateNode}
                    
                />
            )
        })
    }

    addQuestion() {
        if (this.state.newNode==undefined) {
            let newNode = {
                id: uuid.v4(),
                parentNode: this.props.parentNode,
                saved: false, 
                node: {
                    title: {"English": ""}
                }
            };
            this.setState({newNode: newNode});
            console.log('new question added', this.state.newNode)
        }
        console.log('you should already have an empty question');
    }

    addOrUpdateNode(props, nodeId, index) {
        let node;
        let property;
        if (props.hasOwnProperty('node') property='node';
        else property='sub_surveys';
        if (nodeId==this.state.newNode.id) {
            node = Object.assign({}, this.state.newNode[property], properties)
            console.log('adding node', node, index);
            this.props.updateNodeList(node, index);
        } else if (this.props.nodes[index].id==nodeId)
            {
                console.log('updating node', node, index);
                node = Object.assign({}, this.props.nodes[index], properties)
                this.props.updateNodeList(node, index);
            }
        }
        console.log('index wasnt accurate')
    }

    render() {
        console.log('rendering nodelist', this.props.nodes)
        return (
            <div>
                {this.listQuestions()}
                <button 
                    onClick={this.addQuestion}
                    disabled={this.state.newNode}
                >Add Question</button>
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
        if (this.state.title!==this.state.node.title[0]) {
            let properties = {'English': this.state.title};
            this.saveNode(properties);
        }
    }

    deleteNode() {
        /// languages???
    }

    addSubSurvey() {
        let newSubSurvey = {
            parentNode: this.props.node,
            nodes: []
        }
        
        let  = [];
        ss.push(newSubSurvey)
        this.setState({sub_surveys: ss});
        console.log('state subsurveys', this.state.sub_surveys)
        console.log(this.props.node.id)
        this.saveNode({sub_surveys: this.state.sub_surveys});
        this.props.showSubSurvey(newSubSurvey);
    }

    saveNode(updatedProperties) {
        if (updatedProperties) {
            console.log('updated properties', this.props.node.id)
            this.props.addOrUpdateNode(updatedProperties, this.props.node.id);
        } else {
            let newProperties = {
                node: {
                    title: {"English": this.state.title}
                },
                sub_surveys: this.state.sub_surveys
            }
            this.props.addOrUpdateNode(newProperties, this.props.node.id);
        }
        this.setState({isDisabled: false});
    }

    render() {
        return (
            <div>
                Question: <input type="text" placeholder={this.props.node.title[0]}
                    onBlur={this.updateTitle}/>
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