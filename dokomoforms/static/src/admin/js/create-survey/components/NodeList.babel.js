import React from 'react';
import utils from './../utils.js';
import Node from './Node.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { nodeSelector } from './../redux/selectors.babel.js';
import { addNode, addQuestion } from './../redux/actions.babel.js';


function NodeList(props) {

    // constructor(props) {

    //     super(props);

    //     this.listQuestions = this.listQuestions.bind(this);
    //     this.addQuestion = this.addQuestion.bind(this);
    // }

    function listQuestions() {

        console.log('nodes before rendering', props.nodes);

        return props.nodes.map(function(node, index) {
            console.log(node);
            return(
                <Node
                    repeatable={props.repeatable}
                    key={node.id} 
                    id={node.id}
                    index={index+1}
                    sub_surveys={node.sub_surveys}
                    default_language={props.default_language}
                    languages={props.languages}
                />
            );
        });
    }

    function addQuestion() {
        const surveyId = props.nodes[0].survey;
        const nodeId = utils.addId('node');
        props.addQuestion({id: nodeId});
        let newNode = {id: nodeId, survey: surveyId, question: nodeId};
        if (props.repeatable) newNode.repeatable = props.repeatable;
        props.addNode(newNode);
    }

    // render() {
    //     console.log('rendering nodelist', this.props)
    //     console.log('survey id', this.props.survey_id)
    //     return (
    //         <div className="node-list">
    //             <div className="node-list-header">
    //                 Questions
    //             </div>
    //             {this.listQuestions()}
    //             <div style={{textAlign: "center"}}>
    //                 <button 
    //                     onClick={this.addQuestion}
    //                     id="add-question-btn"
    //                 >Add Question</button>
    //             </div>
    //         </div>
    //     );
    // }

    return(
            <div className="node-list">
                <div className="node-list-header">
                    Questions
                </div>
                {listQuestions()}
                <div style={{textAlign: "center"}}>
                    <button 
                        onClick={addQuestion}
                        id="add-question-btn"
                    >Add Question</button>
                </div>
            </div>
    )
}

function mapStateToProps(state){
    console.log('nodelist state');
    return {
        nodes: nodeSelector(state)
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({addNode: addNode, addQuestion: addQuestion}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(NodeList);
