'use strict';

import React from 'react';
import utils from './../utils.js';
import Choice from './subcomponents/Choice.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { orm } from './../redux/models.babel.js';
import { addChoice, updateChoice, deleteChoice, updateQuestion } from './../redux/actions.babel.js';


class MultipleChoiceList extends React.Component {

    constructor(props) {

        super(props);

        this.addChoiceHandler = this.addChoiceHandler.bind(this);
        this.allowOther = this.allowOther.bind(this);
        this.listChoices = this.listChoices.bind(this);

        this.state = {
            allow_other: false
        }
    }

    addChoiceHandler(){
        if (this.props.choices.length < 1) return;
        const newChoice = {id: utils.addId('choice'), question: this.props.questionId};
        this.props.addChoice(newChoice);
    }

    allowOther() {
        this.props.updateQuestion({id: this.props.questionId, allow_other: !this.props.allow_other});
    }


    listChoices(){
        let self = this;
        let choiceList = [];

        if (this.props.choices.length) {
            choiceList = choiceList.concat(this.props.choices)
            let answer;
            if (choiceList.length) {
                choiceList = choiceList.map(function(choice, index){
                    answer = choice.choice_text ? choice.choice_text[self.props.default_language] : "";
                    console.log('choice', choice)
                    return(<Choice
                        key={choice.id}
                        choiceId={choice.id}
                        index={index+1}
                        default_language={self.props.default_language}
                        answer={answer}
                        updateChoice={self.props.updateChoice}
                        deleteChoice={self.props.deleteChoice}
                    />)
                })
            }
        } else {
            choiceList.push(<Choice
                key={1}
                choiceId={0}
                index={1}
                questionId={self.props.questionId}
                default_language={self.props.default_language}
                answer={""}
                addChoice={self.props.addChoice}
                deleteChoice={self.props.deleteChoice}
            />)
            
        }

        if (this.props.choices && this.props.allow_other) {
            console.log('allowing other', this.props.choices)
            choiceList.push(<Choice
                key={0} 
                index={self.props.choices.length}
                answer={"other"}
                editable={false}
                deleteChoice={self.allowOther}
            />)
        }
        return choiceList;
    }


    render() {
        return(
            <div className="multiple-choice-list">
                <div id="multiple-choice-header">Multiple Choice</div>
                <div id="choices">
                    {this.listChoices()}
                </div>
                <div id="multiple-choice-footer">
                    <button id="new-choice"
                        value="new choice"
                        onMouseUp={this.addChoiceHandler}
                    >add choice</button>
                    <button id="allow_other"
                        value="allow other"
                        onClick={this.allowOther}
                        disabled={this.props.allow_other}
                    >allow "other"</button>
                </div>
            </div>
        );
    }
}


function mapStateToProps(state, ownProps){
    const session = orm.session(state.orm);
    console.log(session.Question)

    let choices = session.Question.withId(ownProps.questionId).multiple_choices;

    if (choices) choices = choices.toRefArray();
    else choices = [];

    return {
        choices: choices,
        default_language: state.default_language
    };
}


function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addChoice: addChoice,
        updateChoice: updateChoice,
        deleteChoice: deleteChoice,
        updateQuestion: updateQuestion
    }, dispatch)
}


export default connect(mapStateToProps, matchDispatchToProps)(MultipleChoiceList);
