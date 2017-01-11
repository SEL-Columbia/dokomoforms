import React from 'react';
import utils from './../utils.js';
import ReactDOM from 'react-dom';

class MultipleChoiceList extends React.Component {

    constructor(props) {

        super(props);

        this.listChoices = this.listChoices.bind(this);
        this.addChoice = this.addChoice.bind(this);
        this.updateChoice = this.updateChoice.bind(this);
        this.deleteChoice = this.deleteChoice.bind(this);
        this.changeAddChoice = this.changeAddChoice.bind(this);
        this.save = this.save.bind(this);
        this.allowOther = this.allowOther.bind(this);

        this.state = {
            enableAddChoice: true,
            choices: [],
            saved: false,
            allow_other: false
        }
    }

    componentWillMount(){
        console.log('this is mounting', this.props)
        if (!this.props.choices ||
            !this.props.choices.length) {
            let choiceList = [];
            let newChoice = {id: utils.addId('choice')};
            newChoice['English'] = '';
            console.log(newChoice);
            choiceList.push(newChoice);
            this.setState({choices: choiceList});
        }
        else {
            let choices = [];
            choices = choices.concat(this.props.choices)
            this.setState({choices: choices})
        }
    }

    allowOther() {
        let id;
        let self = this;
        this.setState({allow_other: true}, function(){
            this.props.allowOther(true);
        })

        // let promise = new Promise (function(resolve, reject) {
        //     console.log('inside the promise')
        //     let id = self.addChoice()
        //     resolve(id);
        // })
        
        // promise.then(function(val){
        //     console.log('val', val)
        //     self.updateChoice(val, "other")
        // })
        // console.log('result', this.addChoice())
        // console.log('allow other new id', id)
        // this.updateChoice(id, "other");
    }

    componentWillReceiveProps(nextProps) {

        // if (!this.props.choices ||
        //     !this.props.choices.length) {
        //     let choiceList = [];
        //     let newChoice = {id: utils.addId('choice')};
        //     newChoice[this.props.default_language] = '';
        //     choiceList.push(newChoice);
        //     this.setState({choices: choiceList});
        // }
        // console.log('choices ', this.props)
        // if (!nextProps.choices || !nextProps.choices.length) {
        //     console.log('no')
        //     let choiceList = [];
        //     let newChoice = {id: utils.addId('choice')};
        //     newChoice[this.props.default_language] = '';
        //     choiceList.push(newChoice);
        //     this.setState({choices: choiceList});
        // } else {
        //     console.log('yes')
        //     this.setState({choices: nextProps.choices})
        // }
    }

    shouldComponentUpdate(nextProps, nextState){
        return true;
    }


    listChoices(){
        console.log('rerendering list!!');

        let self = this;
        let choices = [];

        if (this.state.choices) {
            choices = choices.concat(this.state.choices)
        }
        let answer;

        console.log('choices before rendering', choices)
        choices = choices.map(function(choice, index){
            answer = choice['English'];
            return(<Choice
                key={choice.id} 
                index={index+1}
                answer={answer}
                enabled={self.state.enableAddChoice}
                updateChoice={self.updateChoice.bind(null, choice.id)}
                deleteChoice={self.deleteChoice.bind(null, index)}
                changeAddChoice={self.changeAddChoice.bind(null, choice.id)}
                saved={self.state.saved}
            />)
        })

        if (this.state.allow_other) {
            console.log('allowing other')
            choices.push(<Choice
                key={0} 
                index={this.state.choices.length}
                answer={"other"}
                saved={self.state.saved}
            />)
        }

        console.log('after choices', choices)
        return choices;
    }


    addChoice() {
        let choiceList = [];
        choiceList = choiceList.concat(this.state.choices);
        console.log('adding choice', choiceList);
        let newChoice = {id: utils.addId('choice')};
        newChoice['English']='';
        choiceList.push(newChoice);

        this.setState({enableAddChoice: true, choices: choiceList}, function(){
            console.log('new choice added', this.state.choices);
            console.log('newchoice id', newChoice.id)
        });
    }

    updateChoice(id, text) {
        console.log('resolve', id, text)
        let choiceList = [];
        let updated = false;
        choiceList = choiceList.concat(this.state.choices);
        console.log('updating choice', choiceList);

        for (var i=0; i<choiceList.length; i++) {
            if (choiceList[i].id===id) {
                console.log(choiceList[i]['English'], text);
                console.log('its updating');
                choiceList[i]['English']=text;
                updated = true;
                break;
            }
        }

        if (updated===true) {
            this.setState({choices: choiceList}, function(){
                console.log('choice state is now updated', this.state.choices)
                this.props.updateChoices(this.state.choices);
            })
        } else {
            console.log('something went wrong in update');
        }

    }
 
    deleteChoice() {
        console.log('args', arguments)
        const index = arguments[0];
        let choiceList = [];
        let updated = false;
        choiceList = choiceList.concat(this.state.choices);
        choiceList.splice(index, 1)
        this.setState({choices: choiceList})
        this.props.updateChoices(this.state.choices);
    }

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


    render() {

        console.log('rendering choices!!!')

        return(
            <div style={{backgroundColor:'#00a896'}}>
                <h2>multiple choice</h2>
                {this.listChoices()}
                <div>
                    <button id="new-choice"
                        value="new choice"
                        onClick={this.addChoice}
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
        this.rendering = this.rendering.bind(this);

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
        if (event.target.value!==this.state.text ||
            event.target.value!==this.props.answer) {
            console.log('event target', event.target.value)
            console.log('state', this.state.text)
            console.log('props', this.props.answer)
            this.setState({text: event.target.value}, function(){
                console.log('state has been set', this.state.text)
                this.save();
            })
        }
    }


    rendering() {
        console.log("i am rendering!!!", this.props.index, this.props.saved)
    }


    render() {
        console.log('answers!!!!!', this.props)
        return(
            <div>
                {this.rendering()}
                <div className="form-group" style={{backgroundColor:'#daddd8'}}>
                    <div className="row">
                        <label htmlFor="question-title" className="col-xs-2 col-form-label">{this.props.index}.</label>
                        <div className="col-xs-10">
                            <textarea id="choice-text" className="form-control question-title" rows="1"
                                placeholder={this.props.answer} onInput={this.buttonHandler} 
                                onBlur={this.choiceHandler} readOnly={this.props.answer==="other"}/>
                        </div>
                    </div>
                    <button onClick={this.props.deleteChoice}>delete</button>
                </div>
            </div>
        )
    }
}


export default MultipleChoiceList;

