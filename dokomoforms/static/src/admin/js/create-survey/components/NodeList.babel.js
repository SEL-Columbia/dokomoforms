import React from 'react';
import utils from './../utils.js';
import Node from './Node.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {addNode, updateNode, updateSurvey, updateSurveys} from './../redux/actions.babel.js';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.deleteQuestion = this.deleteQuestion.bind(this);
        this.updateNodeOther = this.updateNodeOther.bind(this);
        
        this.state = {
            enableAddNode: false,
            nodes: []
        }
    }


    componentWillMount() {
        console.log(this.props)
        // console.log('addNode', addNode)

        // console.log(this.props.nodes, this.props.survey_nodes)
        // if (!this.props.survey_nodes.length) {
        //     console.log('no survey nodes')
        //     this.addQuestion()
        // }

        // if (!this.props.survey_nodes.length) {

        //     // this.addQuestion()
        //     // let nodeList = [];
        //     // let newNode = {
        //     //     id: utils.addId('node'),
        //     //     node: {}
        //     // };
        //     // // console.log('this is the newnode', newNode)
        //     // // nodeList.push(newNode);
        //     // // this.setState({nodes: nodeList});
        //     // console.log(newNode, this.props.survey_id)

        //     // this.props.addNode(newNode);

        //     // let newSurvey = {};
        //     // console.log('let new survey')
        //     // newSurvey.nodes = []
        //     // newSurvey.nodes.push(newNode.id)
        //     // this.props.updateSurveys(newSurvey, this.props.survey_id)
        // }
    }

    componentWillReceiveProps(nextProps) {
        console.log('will receive props')
        // console.log('props', this.props, nextProps) 
        // if (!this.props.nodes.survey_nodes.length) {
        //     console.log('no survey nodes')
        //     this.addQuestion()
        // }
        // if (this.props.submitting===true) return;
        // if (nextProps.submitting===true) {
        //     console.log('nodelist seeing saved')
        //     return this.props.updateNodeList(this.state.nodes);
        // }
    }


    shouldComponentUpdate(nextProps, nextState) {
        console.log('shouldcompupdate being called!')
        if (nextProps.submitted==true || this.props.submitted==true) {
            return false;
        }
        // if (this.props.nodes.length!=nextProps.nodes.length) return true;
        // if (this.props.default_language!==nextProps.default_language) {
        //     console.log('default language changed');
        //     console.log(this.props.default_language, nextProps.default_language)
        //     return true;
        // }
        // // if (this.state!==nextState) {
        // //     console.log('state change in nodelist');
        // //     return true;
        // // }
        // if (this.props.languages.length!==nextProps.languages.length) {
        //     console.log('question added or deleted');
        //     return true;
        // }
        return true;
    }


    listQuestions() {

        let self = this;
        let node;
        let nodeList = [].concat(this.props.survey_nodes)

        console.log('nodes before rendering', this.props.survey_nodes)

        return nodeList.map(function(node, index) {
            console.log(node)
            return(
                <Node
                    parent={self.props.survey_id}
                    saved={self.props.submitting}
                    key={node.id} 
                    id={node.id}
                    index={index+1}
                    data={node.node}
                    sub_surveys={node.sub_surveys}
                    enabled={self.state.enableAddNode}
                    updateNodeOther={self.updateNodeOther.bind(null, node.id)}
                    deleteQuestion={self.deleteQuestion.bind(null, index)}
                    default_language={self.props.default_language}
                    languages={self.props.languages}
                    showSubSurvey={self.props.showSubSurvey}
                />
            )
        });

        // let nodeList = Object.keys(nodes).map(function(key, index) {
        //     const node = nodes[key];
        //     console.log(node)
        //     return(
        //         <Node
        //             saved={self.props.submitting}
        //             key={node.id} 
        //             id={node.id}
        //             index={index+1}
        //             data={node.node}
        //             enabled={self.state.enableAddNode}
        //             updateNode={self.updateNode.bind(null, node.id)}
        //             deleteQuestion={self.deleteQuestion.bind(null, index)}
        //             default_language={self.props.default_language}
        //             languages={self.props.languages}
        //             showSubSurvey={self.props.showSubSurvey}
        //         />
        //     )
        // });
        // console.log(nodeList);
        // return nodeList;
        // return nodes.map(function(node, index){
        //     // return(
        //     //     <Node
        //     //         saved={self.props.submitting}
        //     //         key={node.id} 
        //     //         id={node.id}
        //     //         index={index+1}
        //     //         data={node.node}
        //     //         enabled={self.state.enableAddNode}
        //     //         updateNode={self.updateNode.bind(null, node.id)}
        //     //         deleteQuestion={self.deleteQuestion.bind(null, index)}
        //     //         default_language={self.props.default_language}
        //     //         languages={self.props.languages}
        //     //         showSubSurvey={self.props.showSubSurvey}
        //     //     />
        //     // )
        // })
    }


    addQuestion() {

        let newNode = {id: utils.addId('node'), node: {}, survey: this.props.survey_id};

        this.props.addNode(newNode)        
        // let nodeList = [];
        // nodeList = nodeList.concat(this.state.nodes);
        // console.log('adding node', nodeList);
        // let newNode = {id: utils.addId('node'), node: {}};
        // nodeList.push(newNode);
        // this.setState({enableAddNode: false, nodes: nodeList}, function(){
        //     console.log('new node added', this.state.nodes);
        // });
        // let newNode = {
        //     id: utils.addId('node'),
        //     node: {}
        // };
        // // console.log('this is the newnode', newNode)
        // // nodeList.push(newNode);
        // // this.setState({nodes: nodeList});
        // this.props.addNode(newNode);

        // let newNode = {
        //         id: utils.addId('node'),
        //         node: {}
        //     };
        //     // console.log('this is the newnode', newNode)
        //     // nodeList.push(newNode);
        //     // this.setState({nodes: nodeList});
        //     console.log(newNode, this.props.survey_id)

        //     this.props.addNode(newNode);

        //     let newSurvey = {};
        //     console.log('let new survey')
        //     newSurvey.nodes = []
        //     if (this.props.survey_nodes) {
        //         console.log('you had survey nodes')
        //         newSurvey.nodes = newSurvey.nodes.concat(this.props.survey_nodes)
        //     }

        //     newSurvey.nodes.push(newNode.id)
        //     this.props.updateSurveys(newSurvey, this.props.survey_id)
    }

    deleteQuestion(index) {
        this.props.delete(node_id)
        // let nodeList = [];
        // nodeList = nodeList.concat(this.props.survey_nodes);
        // nodeList.splice(index, 1);
        // this.setState({nodes: nodeList}, function(){
        //     console.log('node deleted', this.state.nodes);
        //     this.props.removeFromSurveys(type, node, survey_id)
        // })
    }


    updateNodeOther(id, node) {

        this.props.updateNode(id, node, 'node')

        // lext nodeList = [];
        // let updated = false;
        // nodeList = nodeList.concat(this.state.nodes);
        // console.log('updating node', nodeList);

        // for (var i=0; i<nodeList.length; i++) {
        //     if (nodeList[i].id===id) {
        //         console.log(id, node);
        //         console.log('its updating', nodeList)
        //         nodeList[i].node = node;
        //         updated = true;
        //         break;
        //     }
        // }
        // if (updated===true) {
        //     this.setState({nodes: nodeList}, function(){
        //         console.log('node state is now updated', this.state.nodes);
        //         this.props.updateNodeList(this.state.nodes);
        //     })
        // } else {
        //     console.log('something went wrong in update');
        // }
    }


    render() {
        console.log('rendering nodelist', this.props)
        console.log('survey id', this.props.survey_id)
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

// export default NodeList;

function mapStateToProps(state){
    console.log('here')
    console.log(state)
    return {
        surveys: state.surveys,
        nodes: state.nodes,
        surveyView: state.surveyView
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({addNode: addNode,
                                updateNode: updateNode,
                                updateSurvey: updateSurvey,
                                updateSurveys: updateSurveys}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(NodeList);
