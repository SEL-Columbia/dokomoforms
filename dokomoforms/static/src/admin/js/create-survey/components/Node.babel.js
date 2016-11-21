import React from 'react';
import uuid from 'node-uuid';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.deleteQuestion = this.deleteQuestion.bind(this);
        this.addOrUpdateNode = this.addOrUpdateNode.bind(this);
        
        this.state = {
            newNode: null
        }
    }


    componentWillMount() {
        console.log('component will mount');
        console.log('this nodes', this.props.nodes);
        if (this.props.nodes && this.props.nodes.length < 1) {
            let newNode = {id: uuid.v4()};
            console.log('newNodeId', newNode.id)
            this.setState({newNode})
        }
    }


    listQuestions() {
        console.log(this.props.nodes)
        const self = this;

        let rows = [];
        rows = rows.concat(this.props.nodes);
        console.log('rows', rows);
        console.log('props nodes', this.props.nodes);
        if (this.state.newNode) rows.push(this.state.newNode); 
        return rows.map(function(node) {
            return (
                <Node
                    key={node.id}
                    data={node}
                    addOrUpdateNode={self.addOrUpdateNode}
                    language={self.props.language}
                />
            )
        })
    }


    addQuestion() {
        if (this.state.newNode==null) {
            let newNode = {id: uuid.v4()};
            this.setState({newNode: newNode}, function(){
                console.log('new question added', this.state.newNode);
            });
        } else {
            console.log('you should already have an empty question');
        }
    }


    addOrUpdateNode(node, index) {
        if (this.state.newNode && node.id==this.state.newNode.id) {
            console.log('adding node', node, index, -1);
            this.props.updateNodeList(node, -1);
            this.setState({newNode: null}, function() {
                console.log('cleared node');
            })
        } else if (this.props.nodes[index].id==node.id) {
            console.log('index was id')
            console.log('updating node', node, index);
            this.props.updateNodeList(node, index);
        } else {
            let i=0;
            for (i < this.props.nodes.length-1; i++) {
                if (this.node.id==this.props.nodes[i].id {
                    console.log('index was not id');
                    console.log('index', index, 'actual index', i);
                    this.props.updateNodeList(node, i)
                }
            }
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
            title: {},
            hint: {},
            type_constraint: '',
            sub_surveys: []
        }
    }


    componentWillMount() {
        if (Object.keys(this.state.title).length===0) {
            this.setState({title: {this.props.language}: ''})
        }
        if (Object.keys(this.state.hint).length===0) {
            this.setState({hint: {this.props.language}: ''})
        }
    }


    updateTitle(event) {
        if (event.target.value==this.state.title[this.props.default_language]) return;
        let titleObj = {this.props.language: event.target.value}
        this.setState({title: titleObj}, function() {
            console.log('updated title', this.state.title);
            if (this.state.title!==this.props.title) {
                let properties = {this.props.language: this.state.title};
                this.saveNode();
            }
        });
    }

    updateHint(event) {
        if (event.target.value==this.state.hint[this.props.default_language]) return;
        let hintObj = {this.props.language: event.target.value}
        this.setState({hint: hintObj}, function() {
            console.log('updated hint', this.state.hint);
            if (this.state.hint!==this.props.hint) {
                let properties = {this.props.language: this.state.hint};
                this.saveNode();
            }
        });
    }

    addTypeConstraint(event) {

    }


    deleteNode() {
        if (this.props.node.saved==false) {}
    }


    // addSubSurvey(newSubSurvey) {
    //     let sub_surveys = [];
    //     sub_surveys.push(newSubSurvey)
    //     this.setState({sub_surveys: sub_surveys}, function() {
    //         console.log('state subsurveys', this.state.sub_surveys)
    //     });
    //     this.saveNode(this.state.sub_surveys);
    // }


    saveNode(properties) {
        if (properties) {
            console.log('properties to save', properties)
        } else {
            let node = this.state;
            delete node['isDisabled'];
            delete node['sub_surveys'];
            if (JSON.stringify(node)===JSON.stringify(this.props.data.node)) return;
            console.log('reassigning node');
            let updatedNode = Object.assign(this.props.data.node, node);
            this.props.addOrUpdateNode(updatedNode, this.props.index);
        }
        this.setState({isDisabled: false});
    }


    render() {
        let displayTitle = this.props.title[this.props.language]
        let displayHint = this.props.hint[this.props.language]
        return (
            <div>
                Question: <input type="text" placeholder={this.props.title}
                    onBlur={this.updateTitle}/>
                Hint: <input type="text" placeholder={this.props.hint}
                    onBlur={this.updateHint}/>
                <select>
                    {this.createUserDropdown()}
                </select>
                    <button onClick={this.deleteNode}>delete</button>
                    <button onClick={this.saveNode}>save</button>
            </div>
        );
    }
}


export default NodeList;