import React from 'react';
import uuid from 'node-uuid';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.getTitle = this.getTitle.bind(this);
        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.deleteQuestion = this.deleteQuestion.bind(this);
        this.addOrUpdateNode = this.addOrUpdateNode.bind(this);
        this.handleSubSurvey = this.handleSubSurvey.bind(this);
        
        this.state = {
            newNode: null
        }
    }

    componentWillMount() {
        console.log('component will mount');
        console.log('this nodes', this.props.nodes);
        if (this.props.nodes && this.props.nodes.length < 1) {
            let newNode = {
                id: uuid.v4(),
                parentSurvey: this.props.parentSurvey || null,
                saved: false,
                node: {
                    title: {"English": "newest node"}
                }
            }
            console.log('parentSurvey', newNode.parentSurvey);
            console.log('newNodeId', newNode.id)
        this.setState({newNode})
        }
    }

    //temporary. get rid of this
    getTitle(node){
        let key;
        let title;
        for (key in node.node.title) {
            title = node.node.title[key];
        }
        return title;
    }

    handleSubSurvey(subSurvey) {
        console.log("handle SubSurvey", subSurvey);
        this.props.showSubSurvey(subSurvey);
    }

    listQuestions() {
        console.log(this.props.nodes)
        const self = this;

        let rows = [];
        rows = rows.concat(this.props.nodes);
        console.log('rows', rows);
        console.log('props nodes', this.props.nodes);
        if (this.state.newNode) rows.push(this.state.newNode); 
        return rows.map(function(node, i) {
            let title = self.getTitle(node);
            console.log('title?', title)
            console.log('saved?', node.saved, i)
            return (
                <Node
                    key={node.id}
                    index={i}
                    node={node}
                    title={title}
                    addOrUpdateNode={self.addOrUpdateNode}
                    showSubSurvey={self.handleSubSurvey}
                />
            )
        })
    }

    addQuestion() {
        if (this.state.newNode==null) {
            let newNode = {
                id: uuid.v4(),
                parentSurvey: this.props.parentSurvey || null,
                saved: false, 
                node: {
                    title: {"English": "newest node"}
                }
            };
            this.setState({newNode: newNode}, function(){
                console.log('new question added', this.state.newNode)
            });
        } else {
            console.log('you should already have an empty question')
        }
    }

    addOrUpdateNode(newProperties, nodeId, index) {
        console.log(this.props.nodes)
        let node;
        if 
        let property;
        console.log('add or update', newProperties, nodeId, index);
        if (newProperties.hasOwnProperty('node')) {

        } property='node';
        else property='sub_surveys';
        if (this.state.newNode && nodeId==this.state.newNode.id) {
            node = this.state.newNode;
            let properties = Object.assign({}, this.state.newNode[property], newProperties[property])
            console.log('new node?', this.state.newNode[property])
            console.log('props?', newProperties[property])
            console.log('properties?', properties)
            node[property] = properties;
            console.log('adding node', node, -1);
            this.props.updateNodeList(node, -1);
            this.setState({newNode: null}, function() {
                console.log('cleared node');
            })
        }
        else if (this.props.nodes[index].id==nodeId) {
            node = this.props.nodes[index]
            if (node.sub_surveys.length < 1) {
                node.sub_surveys = [];

            }
            console.log(this.props.nodes)
            console.log('you found it', newProperties, nodeId, index)
            console.log('updating node', node, index);

            node[property] = newProperties;
            console.log('properties?', node)
            this.props.updateNodeList(node, index);
        }
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
        if (event.target.value==this.state.title) return;
        this.setState({title: event.target.value}, function() {
            console.log('updated title', this.state.title);
            if (this.state.title!==this.props.title) {
                console.log('same??')
                console.log(this.state.title, this.props.title)
                let properties = {'English': this.state.title};
                this.saveNode();
            }
        });
    }

    deleteNode() {
        if (this.props.node.saved==false) {

        }
    }

    addSubSurvey() {
        let newSubSurvey = {
            parentNode: this.props.node,
            title: 'SUBSURVEY ATTEMPT',
            nodes: []
        }
        let ss = [];
        ss.push(newSubSurvey)
        this.setState({sub_surveys: ss}, function() {
            console.log('state subsurveys', this.state.sub_surveys)
        });
        console.log('?', this.props.node.id);
        this.saveNode(this.state.sub_surveys);
        this.props.handleSubSurvey(newSubSurvey);
    }

    saveNode(updatedProperties) {
        console.log('getting called??')
        if (updatedProperties) {
            console.log(updatedProperties)
            this.props.addOrUpdateNode(updatedProperties, this.props.node.id, this.props.index);
        } else {
            let newProperties = {title: {"English": this.state.title}
        }
        console.log(newProperties);
        this.props.addOrUpdateNode(newProperties, property, this.props.node.id, this.props.index);
        }
        this.setState({isDisabled: false});
    }

    render() {
        return (
            <div>
                Question: <input type="text" placeholder={this.props.title}
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