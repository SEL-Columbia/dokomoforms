import React from 'react';
import NodeList from './NodeList.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {updateSurveyView} from './../redux/actions.babel.js';

// DEFINITION:
// a SUBSURVEY should receive from parent component:
// 1) the question
// 2) the answers that lead to subsurvey
// 3) a callback function to receive subsurvey
// a SUBSURVEY should return:
// 1) a subsurvey object with nodes and buckets

// to do:
// sub-survey should probably display the question and answer(s) that
// leads to it
// should user choose bucket on this page or node page?

class SubSurvey extends React.Component {

    constructor(props) {
        super(props);

        this.viewHandler = this.viewHandler.bind(this)

        this.state = {
            buckets: [],
            nodes: []
        };
    }

    viewHandler(){
        this.props.updateSurveyView(this.props.nodeId, this.props.previous, null)
    }

    render() {
        let q = this.props.nodes[this.props.nodeId].node.title.English;
        console.log(q)
        console.log('from the new view', this.props)
        return (
            <div className="container">
                <div className="col-lg-8 survey center-block">
                    <div className="survey-header header">
                        Create a Sub Survey
                    </div>

                    <div>
                        Question: {q}
                        {(this.props.survey.buckets[0].type_constraint=='multiple_choice') &&
                            <span>Answer: {this.props.survey.buckets[0].choice_number}</span>
                        }
                    </div>
                    
                    <NodeList
                        key={this.props.survey.id}
                        submitted={this.props.submitted}
                        survey_id={this.props.survey.id}
                        survey_nodes={this.props.survey.nodes}
                        languages={this.props.languages}
                    />
                </div>
                <button onClick={this.viewHandler}>back</button>
            </div>
        );
    }

}

function mapStateToProps(state){
    console.log('here')
    console.log(state)
    return {
        surveys: state.surveys,
        nodes: state.nodes
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({updateSurveyView: updateSurveyView}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(SubSurvey);

// export default SubSurvey;

