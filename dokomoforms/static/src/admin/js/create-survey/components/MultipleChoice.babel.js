import React from 'react';
import utils from './../utils.js';
import ReactDOM from 'react-dom';

class MultipleChoiceList extends React.Component {

    constructor(props) {

        super(props);

        this.listChoices = this.listChoices.bind(this);
        this.addChoice = this.addChoice.bind(this);
        this.updateChoice = this.updateChoice.bind(this);
        this.changeAddChoice = this.changeAddChoice.bind(this);
        this.save = this.save.bind(this);

        this.state = {
            enableAddChoice: false,
            choices: [],
            saved: false
        }
    }


    componentWillMount() {
        if (!this.props.choices ||
            !this.props.choices.length) {
            let choiceList = [];
            let newChoice = {id: utils.addId('choice')};
            newChoice[this.props.default_language] = '';
            choiceList.push(newChoice);
            this.setState({choices: choiceList});
        }
    }


    listChoices(){
        console.log('rerendering list!!');

        let self = this;
        let choices = this.state.choices;
        let answer;

        console.log('choices before rendering', choices)
        return choices.map(function(choice, index){
            answer = choice[self.props.default_language];
            return(<Choice
                key={choice.id} 
                index={index+1}
                answer={answer}
                enabled={self.state.enableAddChoice}
                updateChoice={self.updateChoice.bind(null, choice.id)}
                changeAddChoice={self.changeAddChoice.bind(null, choice.id)}
                saved={self.state.saved}
            />)
        })
    }


    addChoice() {

        let choiceList = [];
        choiceList = choiceList.concat(this.state.choices);
        console.log('adding choice', choiceList);
        let newChoice = {id: utils.addId('choice')};
        newChoice[this.props.default_language]='';
        choiceList.push(newChoice);
        this.setState({enableAddChoice: false, choices: choiceList}, function(){
            console.log('new choice added', this.state.choices);
        });
    }


    updateChoice(id, text) {
        let choiceList = [];
        let updated = false;
        choiceList = choiceList.concat(this.state.choices);
        console.log('updating choice', choiceList);

        for (var i=0; i<choiceList.length; i++) {
            if (choiceList[i].id===id) {
                console.log(choiceList[i][this.props.default_language], text)
                console.log('its updating')
                choiceList[i][this.props.default_language]=text;
                updated = true;
                break;
            }
        }

        if (updated===true) {
            this.setState({choices: choiceList}, function(){
                console.log('choice state is now updated', this.state.choices);
            })
        } else {
            console.log('something went wrong in update');
        }

    }
 

    changeAddChoice(id){
        console.log('!!!!!!!!')
        console.log(this.state.choices)
        console.log('!!!!!!!!')

        let choice;
        for (var i=0; i<this.state.choices.length; i++) {
            choice=this.state.choices[i]
            console.log(choice);
            if (!choice[this.props.default_language].length &&
                choice.id!==id) return;
        }
        let previous = this.state.enableAddChoice;
        this.setState({enableAddChoice: !previous});
    }


    save(){
        let previous = this.state.saved;
        this.setState({saved: !previous});
    }


    render() {

        return(
            <div style={{backgroundColor:'#00a896'}}>
                <h2>multiple choice</h2>
                {this.listChoices()}
                <button id="new-choice"
                    value="new choice"
                    onClick={this.addChoice}
                    disabled={!this.state.enableAddChoice}
                >add choice</button>
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
        if (this.props.saved!==nextProps.saved) return true;
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
        return(
            <div>
                {this.rendering()}
                <div className="form-group" style={{backgroundColor:'#02c39a'}}>
                    <div className="row">
                        <label htmlFor="question-title" className="col-xs-2 col-form-label">{this.props.index}.</label>
                        <div className="col-xs-10">
                            <textarea id="choice-text" className="form-control question-title" rows="1" defaultValue={this.props.answer} onInput={this.buttonHandler} onBlur={this.choiceHandler} readOnly={this.props.saved}/>
                        </div>
                    </div>
                    <button>delete</button>
                </div>
            </div>
        )
    }
}


export default MultipleChoiceList;

