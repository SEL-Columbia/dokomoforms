import React from 'react';
import utils from './../utils.js';
import Node from './Node.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {nodeSelector} from './../redux/selectors.babel.js';
import {addNode, addQuestion} from './../redux/actions.babel.js';


class NodeList extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);
        this.addQuestion = this.addQuestion.bind(this);

    }


    listQuestions() {

        let self = this;

        console.log('nodes before rendering', this.props.nodes)

        return this.props.nodes.map(function(node, index) {
            console.log(node)
            return(
                <Node
                    repeatable={self.props.repeatable}
                    key={node.id} 
                    id={node.id}
                    index={index+1}
                    data={node.question}
                    sub_surveys={node.sub_surveys}
                    default_language={self.props.default_language}
                    languages={self.props.languages}
                />
            )
        });
    }


    addQuestion() {
        const surveyId = this.props.nodes[0].survey;
        const nodeId = utils.addId('node');
        let newNode = {id: nodeId, survey: surveyId};
        if (this.props.repeatable) newNode.repeatable = this.props.repeatable;
        this.props.addQuestion({id: nodeId});
        this.props.addNode(newNode);
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
