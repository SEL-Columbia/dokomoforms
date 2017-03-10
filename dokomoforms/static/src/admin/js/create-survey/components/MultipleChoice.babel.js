import React from 'react';
import utils from './../utils.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { orm } from './../redux/models.babel.js';
import { addChoice, updateChoice, deleteChoice, updateQuestion } from './../redux/actions.babel.js';


function MultipleChoiceList(props) {

    // constructor(props) {

    //     super(props);

    //     this.listChoices = this.listChoices.bind(this);
    //     // this.updateChoice = this.updateChoice.bind(this);
    //     // this.deleteChoice = this.deleteChoice.bind(this);
    //     // this.changeAddChoice = this.changeAddChoice.bind(this);
    //     this.addChoiceHandler = this.addChoiceHandler.bind(this);
    //     this.allowOther = this.allowOther.bind(this);

    //     this.state = {
    //         enableAddChoice: true,
    //         allow_other: false
    //     }
    // }


    function componentWillMount(){
        console.log(props.choices)
        if (!props.choices.length) {
            console.log('adding first choice')
            addChoiceHandler();
        };
    }


    function allowOther() {
        props.updateQuestion({id: props.questionId, allow_other: !props.allow_other});
    }


    function addChoiceHandler(){
        let newChoice = {id: utils.addId('choice'), question: props.questionId};
        props.addChoice(newChoice);
    }


    function listChoices(){
        console.log('rerendering choice list');

        // let self = this;
        let choiceList = [];

        if (props.choices.length) {
            console.log('it has choices', props)
            choiceList = choiceList.concat(props.choices)
        } else {
            addChoiceHandler();
        }

        let answer;
        if (choiceList.length) {
            choiceList = choiceList.map(function(choice, index){
                answer = choice.choice_text ? choice.choice_text['English'] : "";
                console.log('choice', choice)
                return(<Choice
                    key={choice.id}
                    choiceId={choice.id}
                    index={index+1}
                    answer={answer}
                    updateChoice={props.updateChoice}
                    deleteChoice={props.deleteChoice}
                />)
            })
        }

        if (props.choices && props.allow_other) {
            console.log('allowing other')
            choiceList.push(<Choice
                key={0} 
                index={props.choices.length}
                answer={"other"}
                editable={false}
                deleteChoice={allowOther}
            />)
        }
        return choiceList;
    }

    return(
        <div style={{backgroundColor:'#447785'}}>
            <h2>multiple choice</h2>
            {listChoices()}
            <div>
                <button id="new-choice"
                    value="new choice"
                    onMouseDown={addChoiceHandler}
                >add choice</button>
                <button id="allow_other"
                    value="allow other"
                    onClick={allowOther}
                    disabled={props.allow_other}
                >allow "other"</button>
            </div>
        </div>
    )
}


function Choice(props) {

    // constructor(props){
    //     super(props);

    //     this.choiceHandler = this.choiceHandler.bind(this);
    //     this.buttonHandler = this.buttonHandler.bind(this);

    //     this.state = {
    //         editable: true
    //     }
    // }


    // shouldComponentUpdate(nextProps, nextState) {
    //     if (this.props.answer!==nextProps.answer) {
    //         console.log('not the same!')
    //         return true;
    //     }
    //     console.log('props choices', this.props.answer, nextProps.answer)
    //     return false;
    // }
    

    // buttonHandler(event) {
    //     console.log('button handler', this.props.enabled)
    //     if (!this.props.enabled && event.target.value.length ||
    //         this.props.enabled && !event.target.value.length) {
    //             console.log('enabled updated')
    //             this.props.changeAddChoice();
    //     }
    // }


    function choiceHandler(event) {
        console.log('choice handler', event.target.value);
        if (!event.target.value.length) return;
        let choice = {id: props.choiceId, choice_text: {'English': event.target.value}};
        props.updateChoice(choice);
    }


    console.log('choice props', props)
    return(
        <div>
            <div className="form-group" style={{backgroundColor:'#daddd8'}}>
                <div className="row">
                    <label htmlFor="question-title" className="col-xs-2 col-form-label">{props.index}.</label>
                    <div className="col-xs-10">
                        <textarea id="choice-text" className="form-control question-title" rows="1"
                            defaultValue={props.answer} onBlur={choiceHandler}
                            readOnly={props.answer==="other"}/>
                    </div>
                </div>
                {(props.deleteChoice) &&
                    <button
                    onClick={props.deleteChoice.bind(null, props.choiceId)}>delete</button>
                }
            </div>
        </div>
    )
}


function mapStateToProps(state, ownProps){
    const session = orm.session(state.orm);
    console.log('ownProps', ownProps)

    console.log('state dot orm', session)
    console.log(session.Question)

    let choices = session.Question.withId(ownProps.questionId).multiple_choices;

    if (choices) choices = choices.toRefArray();
    else choices = [];

    console.log('the choices mc', choices);

    return {
        choices: choices
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
