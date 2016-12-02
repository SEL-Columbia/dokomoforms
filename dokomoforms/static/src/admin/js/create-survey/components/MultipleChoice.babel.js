import React from 'react';
import utils from './../utils.js';
import ReactDOM from 'react-dom';

class MultipleChoiceList extends React.Component {

    constructor(props) {

        super(props);

        this.listChoices = this.listChoices.bind(this);
        this.addChoice = this.addChoice.bind(this);
        this.changeAddChoice = this.changeAddChoice.bind(this);
        this.save = this.save.bind(this);

        this.state = {
            enableAddChoice: false,
            choices: [],
            saved: false
        }
    }

    listChoices(){
        console.log('rerendering list!!');

        let self = this;
        let choices = this.state.choices;
        let answer;

        if (!choices.length) {
            let newChoice = {id: utils.addId('choice')};
            newChoice[this.props.default_language] = '';
            choices.push(newChoice);
        }

        console.log('choices before rendering', choices)
        return choices.map(function(choice, i){
            answer = choice[self.props.default_language];
            return(<Choice
                key={choice.id} 
                index={i+1}
                answer={answer}
                enabled={self.state.enableAddChoice}
                addChoice={self.addChoice.bind(null, choice.id)}
                changeAddChoice={self.changeAddChoice}
                saved={self.state.saved}
            />)
        })
    }

    addChoice(id, event) {

        console.log('initial choice state', this.state.choices);
        console.log('id', id);
        console.log('event', event.target)

        let updated = false;
        let choiceList = [];
        choiceList = choiceList.concat(this.state.choices);
        // if add choice was clicked, create empty choice
        if (id===-1) {
            console.log('its -1');
            let newChoice = {id: utils.addId('choice')};
            newChoice[this.props.default_language]='';
            choiceList.push(newChoice);
            updated = true;
            this.setState({enableAddChoice: false});
            console.log('new choiceList', choiceList);
        // if adding the first choice in list
        } else if (!choiceList.length) {
            console.log('empty choiceList', choiceList);
            let newChoice = {
                id: id, 
                [this.props.default_language]: event.target.value
            }
            choiceList.push(newChoice);
            updated = true;
            console.log('its adding');
        } else {
            for (var i = 0; i<choiceList.length; i++) {
                console.log('first', choiceList[i].id, id)
                // if updating an existing choice
                if (choiceList[i].id===id) {
                    console.log(choiceList[i][this.props.default_language], event.target.value)
                    console.log('its updating')
                    choiceList[i][this.props.default_language]=event.target.value;
                    updated = true;
                    break;
                    console.log('after update');
                }
            }
        }
        if (updated===true) {
            this.setState({choices: choiceList}, function(){
                console.log('choice state is now updated', this.state.choices);
            });
        }
    }


    changeAddChoice(){
        let previous = this.state.enableAddChoice;
        this.setState({enableAddChoice: !previous});
    }


    save(){
        this.setState({saved: true});
    }


    render() {

        return(
            <div style={{backgroundColor:'#00a896'}}>
                <h2>multiple choice</h2>
                {this.listChoices()}
                <button id="new-choice"
                    value="new choice"
                    onClick={this.addChoice.bind(null, -1)}
                    disabled={!this.state.enableAddChoice}
                >add choice</button>
                <button id="save-choices"
                    value="save choices"
                    onClick={this.save}
                    disabled={!this.state.enableAddChoice}
                >save</button>
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


    save() {
        console.log('testing save!!');
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
        console.log('this is a test')
        if (event.target.value!==this.state.text) {
            this.setState({text: event.target.value})
        }
        // console.log(props.answer, event.target.value)
        // if (event.target.value===props.answer) return;
        // else props.addChoice(event);
    }


    rendering(){
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
                            <textarea id="choice-text" className="form-control question-title" rows="1" defaultValue={this.props.answer} onInput={this.buttonHandler} onBlur={this.choiceHandler}/>
                        </div>
                    </div>
                    <button>delete</button>
                </div>
            </div>
        )
    }
}


export default MultipleChoiceList;

