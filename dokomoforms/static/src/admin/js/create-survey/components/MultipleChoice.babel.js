import React from 'react';
import utils from './../utils.js';
import ReactDOM from 'react-dom';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {orm} from './../redux/models.babel.js';
import {addChoice, updateChoice, deleteChoice} from './../redux/actions.babel.js';


class MultipleChoiceList extends React.Component {

    constructor(props) {

        super(props);

        this.listChoices = this.listChoices.bind(this);
        // this.updateChoice = this.updateChoice.bind(this);
        // this.deleteChoice = this.deleteChoice.bind(this);
        // this.changeAddChoice = this.changeAddChoice.bind(this);
        // this.save = this.save.bind(this);
        this.addChoiceHandler = this.addChoiceHandler.bind(this);
        this.allowOther = this.allowOther.bind(this);

        this.state = {
            enableAddChoice: true,
            choices: [],
            saved: false,
            allow_other: false
        }
    }


    componentWillMount(){
        if (!this.props.choices.length) {
            this.addChoiceHandler({question: this.props.questionId})
        }
    }


    allowOther() {
        let id;
        let self = this;
        this.setState({allow_other: true})
    }


    shouldComponentUpdate(nextProps, nextState){
        return true;
    }


    addChoiceHandler(){
        let newChoice = {question: this.props.questionId};
        this.props.addChoice(newChoice);
    }


    listChoices(){
        console.log('rerendering list!!');

        let self = this;
        let choiceList = [];

        if (this.props.choices.length) {
            console.log('it has choices', this.props)
            choiceList = choiceList.concat(this.props.choices)
        }

        let answer;
        if (choiceList.length) {
            choiceList = choiceList.map(function(choice, index){
                answer = choice['English'] || "";
                console.log('choice', choice)
                return(<Choice
                    key={choice.id} 
                    index={index+1}
                    answer={answer}
                    enabled={self.state.enableAddChoice}
                    addOrUpdateChoice={self.props.updateChoice}
                    deleteChoice={self.props.deleteChoice}
                    changeAddChoice={self.changeAddChoice.bind(null, choice.id)}
                    choiceId={choice.id}
                    questionId={self.props.questionId}
                />)
            })
        }

        if (this.props.choices && this.state.allow_other) {
            console.log('allowing other')
            choiceList.push(<Choice
                key={0} 
                index={this.props.choices.length}
                answer={"other"}
            />)
        }
        return choiceList;
    }


    // addChoice() {
    //     let choiceList = [];
    //     choiceList = choiceList.concat(this.state.choices);
    //     console.log('adding choice', choiceList);
    //     let newChoice = {id: utils.addId('choice')};
    //     newChoice['English']='';
    //     choiceList.push(newChoice);

    //     this.setState({enableAddChoice: true, choices: choiceList}, function(){
    //         console.log('new choice added', this.state.choices);
    //         console.log('newchoice id', newChoice.id)
    //     });
    // }


    // updateChoice(id, text) {
    //     console.log('resolve', id, text)
    //     let choiceList = [];
    //     let updated = false;
    //     choiceList = choiceList.concat(this.state.choices);
    //     console.log('updating choice', choiceList);

    //     for (var i=0; i<choiceList.length; i++) {
    //         if (choiceList[i].id===id) {
    //             console.log(choiceList[i]['English'], text);
    //             console.log('its updating');
    //             choiceList[i]['English']=text;
    //             updated = true;
    //             break;
    //         }
    //     }

    //     if (updated===true) {
    //         this.setState({choices: choiceList}, function(){
    //             console.log('choice state is now updated', this.state.choices)
    //             this.props.updateChoices(this.state.choices);
    //         })
    //     } else {
    //         console.log('something went wrong in update');
    //     }
    // }
 

    // deleteChoice() {
    //     console.log('args', arguments)
    //     const index = arguments[0];
    //     let choiceList = [];
    //     let updated = false;
    //     choiceList = choiceList.concat(this.state.choices);
    //     choiceList.splice(index, 1)
    //     this.setState({choices: choiceList})
    //     this.props.updateChoices(this.state.choices);
    // }


    changeAddChoice(id){
        return;
        // console.log('!!!!!!!!')
        // console.log(this.state.choices)
        // console.log('!!!!!!!!')

        // let choice;
        // for (var i=0; i<this.state.choices.length; i++) {
        //     choice=this.state.choices[i]
        //     console.log(choice);
        //     if (!choice[this.props.default_language].length &&
        //         choice.id!==id) return;
        // }
        // let previous = this.state.enableAddChoice;
        // this.setState({enableAddChoice: !previous});
    }


    save(){
        let previous = this.state.saved;
        this.setState({saved: !previous});
    }


    render(){
        return(
            <div style={{backgroundColor:'#00a896'}}>
                <h2>multiple choice</h2>
                {this.listChoices()}
                <div>
                    <button id="new-choice"
                        value="new choice"
                        onMouseDown={this.addChoiceHandler}
                        disabled={!this.state.enableAddChoice}
                    >add choice</button>
                    <button id="allow_other"
                        value="allow other"
                        onClick={this.allowOther}
                        disabled={this.state.allow_other}
                    >allow "other"</button>
                </div>
            </div>
        )
    }
}


class Choice extends React.Component {

    constructor(props){
        super(props);

        this.choiceHandler = this.choiceHandler.bind(this);
        this.buttonHandler = this.buttonHandler.bind(this);

        this.state = {
            text: '',
            editable: true
        }
    }


    componentWillReceiveProps(nextProps, nextState) {
        console.log('will receive props');
        console.log(nextProps);
        if (nextProps.saved===true) {
            console.log('true')
            this.setState({editable: false}, function(){
                this.save()
            })
        };
    }


    shouldComponentUpdate(nextProps, nextState) {
        if (this.props.answer!==nextProps.answer) {
            console.log('not the same!')
            return true;
        }
        console.log('props choices', this.props.answer, nextProps.answer)
        return false;
    }


    save() {
        console.log('testing save!!', this.state.text);
        if (this.state.text===this.props.answer) return;
        else this.props.updateChoice(this.state.text);
    }
    

    buttonHandler(event) {
        console.log('button handler', this.props.enabled)
        if (!this.props.enabled && event.target.value.length ||
            this.props.enabled && !event.target.value.length) {
                console.log('enabled updated')
                this.props.changeAddChoice();
        }
    }


    choiceHandler(event) {
        // if (event.target.value!==this.state.text ||
        //     event.target.value!==this.props.answer) {
        //     console.log('event target', event.target.value)
        //     console.log('state', this.state.text)
        //     console.log('props', this.props.answer)
        //     this.setState({text: event.target.value}, function(){
        //         console.log('state has been set', this.state.text)
        //         this.save();
        //     })
        // }
        console.log('choice handler')
        if (!event.target.value.length) return;
        let question = {id: this.props.choiceId, 'English': event.target.value};
        this.props.addOrUpdateChoice(question);
    }


    render() {
        console.log('props', this.props)
        return(
            <div>
                <div className="form-group" style={{backgroundColor:'#daddd8'}}>
                    <div className="row">
                        <label htmlFor="question-title" className="col-xs-2 col-form-label">{this.props.index}.</label>
                        <div className="col-xs-10">
                            <textarea id="choice-text" className="form-control question-title" rows="1"
                                placeholder={this.props.answer} onInput={this.buttonHandler} 
                                onBlur={this.choiceHandler} readOnly={this.props.answer==="other"}/>
                        </div>
                    </div>
                    {(this.props.deleteChoice) &&
                        <button onClick={this.props.deleteChoice.bind(null, this.props.choiceId)}>delete</button>
                    }
                </div>
            </div>
        )
    }
}


function mapStateToProps(state, ownProps){
    const session = orm.session(state.orm);
    console.log('ownProps', ownProps)

    console.log('state dot orm', session)
    console.log(session.Question)

    let choices = session.Question.withId(ownProps.questionId).multiple_choices;

    if (choices) choices = choices.toRefArray();
    else choices = [];

    console.log(choices);
    return {
        choices: choices
    };
}


function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addChoice: addChoice,
        updateChoice: updateChoice,
        deleteChoice: deleteChoice
    }, dispatch)
}


export default connect(mapStateToProps, matchDispatchToProps)(MultipleChoiceList);
