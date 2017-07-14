import React from 'react';
import utils from './../utils.js';
import MultipleChoice from './MultipleChoice.babel.js';
import Logic from './Logic.babel.js';
import Fields from './Fields.babel.js';
import SubSurveyList from './SubSurveyList.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { orm } from './../redux/models.babel.js';
import { addSurvey, addNode, updateNode, addQuestion, updateQuestion, updateCurrentSurvey, deleteLogic, deleteNode } from './../redux/actions.babel.js';

class Node extends React.Component {

    constructor(props) {
        super(props);

        this.getTitleOrHintValue = this.getTitleOrHintValue.bind(this);
        this.updateTitle = this.updateTitle.bind(this);
        this.updateHint = this.updateHint.bind(this);
        this.addNumber = this.addNumber.bind(this);
        this.addTypeConstraint = this.addTypeConstraint.bind(this);
        this.addAllowMultiple = this.addAllowMultiple.bind(this);
        this.addSubSurvey = this.addSubSurvey.bind(this);
        this.showSubSurveys = this.showSubSurveys.bind(this);
        this.listTitles = this.listTitles.bind(this);
        this.listHints = this.listHints.bind(this);
        this.allowOther = this.allowOther.bind(this);
        // this.toggleField = this.toggleField.bind(this);
        this.deleteNodeHandler = this.deleteNodeHandler.bind(this);

        this.state = {
            showHint: false,
            showLogic: false,
            sub_surveys: [],
            showSubSurveys: false,
            allow_multiple: "false"
        }
    }


    componentWillReceiveProps(nextProps) {
        console.log('will receive props node', this.props.repeatable, nextProps.repeatable)
        if (nextProps.repeatable=="true" && this.props.repeatable!="true") this.props.updateNode({id: this.props.id, repeatable: "true"})
        if (nextProps.repeatable=="false" && this.props.repeatable!="false") this.props.updateNode({id: this.props.id, repeatable: "false"})
    }


    getTitleOrHintValue(property, language) {
        console.log('title or hint value', this.props.question)
        if (!this.props.question ||
            !this.props.question[property]) return '';
        else return this.props.question[property][language];
    }


    showSubSurveys() {
        this.setState({showSubSurveys: true})
    }


    addSubSurvey() {
        const nodeId = utils.addId('node');
        const surveyId = utils.addId('survey');
        const newSubSurvey = {
            id: surveyId, 
            node: this.props.id
        };
        const newNode = {
            id: nodeId,
            survey: newSubSurvey.id
        };
        const newQuestion = {
            id: nodeId
        };
        console.log('ss from node')
        this.props.addSurvey(newSubSurvey);
        this.props.addNode(newNode);
        this.props.addQuestion(newQuestion);
    }


    listTitles(){

        const self = this;
        let displayQuestion, key;

        return this.props.languages.map(function(language){
            console.log('language', language);
            displayQuestion = self.getTitleOrHintValue('title', language);
            console.log('display', displayQuestion)
            key = language.toString()
            return (
                <div key={language} className="survey-group">
                    <Title
                        property={'Question'}
                        key={key+"_t"}
                        language={language}
                        display={displayQuestion}
                        update={self.updateTitle.bind(null, language)}
                    />
                </div>
            )
        }) 
    }


    listHints(){

        const self = this;
        let displayHint, key;

        return this.props.languages.map(function(language){
            console.log('language', language);
            displayHint = self.getTitleOrHintValue('hint', language);
            console.log('display', displayHint)
            key = language.toString()
            return (
                <div key={language} className="survey-group">
                    <span className="language-header">{language}</span>
                    <Title
                        property={'Hint'}
                        key={key+"_h"}
                        language={language}
                        display={displayHint}
                        update={self.updateHint.bind(null, language)}
                    />
                </div>
            )
        }) 
    }


    updateTitle(property, event) {
        console.log('title', event.target.value);
        // const titleObj = {title: {English: event.target.value}};
        // const updatedQuestion = Object.assign({id: this.props.question.id}, titleObj);
        // console.log('updated question', updatedQuestion);
        this.props.updateQuestion({id: this.props.question.id, title: {English: event.target.value}});
    }


    updateHint(property, event) {
        const hintObj = {hint: {English: event.target.value}};
        const updatedQuestion = Object.assign({id: this.props.question.id}, hintObj);
        console.log('updating question', updatedQuestion)
        this.props.updateQuestion(updatedQuestion);
    }


    addTypeConstraint(value) {
        console.log('add type constraint', value)
        this.props.updateQuestion({id: this.props.question.id, type_constraint: value});
        // this is here to make sure there aren't existing bounds
        // that are no longer compatible
        this.setState({showLogic: false}, ()=>{
            if (this.props.showLogic) this.props.deleteLogic(this.props.question.id);
        });
    }


    addNumber(event) {
        console.log('updating number', event.target.value);
        this.props.updateQuestion({id: this.props.question.id, number: event.target.value});
    }


    addAllowMultiple(event) {
        console.log('event target', event.target.value)
        this.props.updateQuestion({id: this.props.question.id, allow_multiple: event.currentTarget.value})
    }


    allowOther(value) {
        this.props.updateQuestion({id: this.props.node.id, allow_other: value});
    }


    deleteNodeHandler(){
        console.log('the props', this.props);
        setTimeout(()=>(this.props.deleteNode(this.props.question.id)), 150);
    }

    // toggleField(field){
    //     console.log('togglefield', field, this.state[field])
    //     this.setState({[field]: !this.state[field]})
    // }


    render() {
        console.log('node props', this.props)

        const number = (this.props.question.number) ? this.props.question.number : "";

        return (
            <div className="node">
                <div className="custom-number">
                    Number : <input id="number-box" className="form-control" onBlur={this.addNumber} defaultValue={number}></input>
                </div>
                <div>
                    {this.listTitles()}
                </div>
                <hr />
                <div className="survey-group" style={{marginTop: "30px"}}>
                    <div className="survey-double-column">
                        <TypeConstraint 
                            addTypeConstraint={this.addTypeConstraint}
                            type_constraint={this.props.question.type_constraint}
                        />
                    </div>
                    <div className="survey-double-column">
                        <MultipleResponse 
                            addAllowMultiple={this.addAllowMultiple}
                            allow_multiple={this.props.question.allow_multiple || this.state.allow_multiple}
                            id={this.props.id}/>
                    </div>
                </div>

                <div>
                    {(this.props.question.type_constraint==="multiple_choice") &&
                        <MultipleChoice
                            questionId={this.props.question.id}
                            allow_other={this.props.question.allow_other || false}
                            default_language={this.props.default_language}
                        />
                    }
                </div>


                {(this.state.showHint || this.props.question.hint) &&
                    <div>
                        <hr />
                        {this.listHints()}
                    </div>
                }


                {(this.props.showLogic || this.state.showLogic) &&
                    <div>
                        <hr />
                        <Logic type_constraint={this.props.question.type_constraint} id={this.props.id}/>
                    </div>
                }


                {(this.props.sub_surveys && this.props.sub_surveys.length > 0) &&
                    <div>
                        <hr />
                        <SubSurveyList
                            type_constraint={this.props.question.type_constraint}
                            sub_surveys={this.props.sub_surveys}
                            question_id={this.props.id}
                            addSubSurvey={this.addSubSurvey}
                            goToSubSurvey={this.goToSubSurvey}
                        />
                    </div>
                }


                <Fields toggleField={(field => this.setState({[field]: !this.state[field]}))}
                    showHint={this.state.showHint || this.props.question.hint}
                    showSubSurveys={(typeof this.props.question.title!=='undefined')}
                    addSubSurvey={this.addSubSurvey}
                    deleteNode={this.deleteNodeHandler}
                    type_constraint={this.props.question.type_constraint}
                />
            </div>
        );
    }
}


function Title(props) {
    console.log('title', props)
    return(
        <div className="title form-group">
            <label htmlFor="question-title" className="col-xs-4 col-form-label">{props.property}:</label>
            <textarea className="form-control question-title" rows="1" defaultValue={props.display}
                onBlur={props.update.bind(props.property)}/>
        </div>
    )
}


function MultipleResponse(props) {
    console.log('multiple response', props)
    const name = "allow-multiple" + props.id.toString();
    return(
        <div>
            <label className="col-form-label double-column-label">Allow Multiple Responses:</label>
            <div className="multiple-response">
                <div className="allow-multiple">
                    <input type="radio" name={name} value={"true"} onChange={props.addAllowMultiple} checked={props.allow_multiple==="true"}/>
                    <label>Yes</label>
                </div>
                <div className="allow-multiple">
                    <input type="radio"
                            name={name} value={"false"}
                            onChange={props.addAllowMultiple}
                            checked={props.allow_multiple==="false"}
                    />
                    <label>No</label>
                </div>
            </div>
        </div>
    )
}


function TypeConstraint(props) {

    function addTypeConstraint(value) {
        console.log('add type constraint', value)
        const node = this.props.data;
        const updatedQuestion = Object.assign({id: this.props.question.id, type_constraint: value});
        // console.log('updated node', updatedNode, this.props)
        this.props.updateQuestion(updatedQuestion);
        // this.props.updateNode(this.props.id, {type_constraint: event.target.value})
    }

    function updateTypeConstraint(event) {
        console.log('update type', event.target.getAttribute('value'));
        let type_constraint = event.target.getAttribute('value');
        if (this.props.question.logic) 
        props.addTypeConstraint(type_constraint);
    }

    function renderList() {

        let currentType = props.type_constraint;
        if (currentType==="multiple_choice") currentType = "multiple choice";

        return (
            <div className="dropdown-test">
                <label htmlFor="type-constraint" className="col-form-label double-column-label">Question Type:</label>
                <button className="form-control type-constraint">
                    <span style={{float: "left"}}>{currentType}</span>
                    <span className="glyphicon glyphicon-menu-down" aria-hidden="true" style={{float: "right"}}></span>
                </button>
                <div className="dropdown-content">
                    <a value="text" onClick={updateTypeConstraint}>text</a>
                    <a value="photo" onClick={updateTypeConstraint}>photo</a>
                    <a value="integer" onClick={updateTypeConstraint}>integer</a>
                    <a value="decimal" onClick={updateTypeConstraint}>decimal</a>
                    <a value="date" onClick={updateTypeConstraint}>date</a>
                    <a value="time" onClick={updateTypeConstraint}>time</a>
                    <a value="timestamp" onClick={updateTypeConstraint}>timestamp</a>
                    <a value="location" onClick={updateTypeConstraint}>location</a>
                    <a value="facility" onClick={updateTypeConstraint}>facility</a>
                    <a value="multiple_choice" onClick={updateTypeConstraint}>multiple choice</a>
                    <a value="note" onClick={updateTypeConstraint}>note</a>
                </div>
            </div>
        )
    }
    return renderList();
}


function mapStateToProps(state, ownProps){
    console.log('here', ownProps);
    console.log(state);

    const session = orm.session(state.orm);

    console.log('state dot orm', session)
    console.log(session.Question)

    const question = session.Question.withId(ownProps.id);

    const showLogic = session.Question.withId(ownProps.id).logic!==null;

    const questionObj = Object.assign({}, question.ref);

    console.log('question from node!', questionObj)

    return {
        question: questionObj,
        showLogic: showLogic
    };
}


function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addSurvey: addSurvey,
        updateNode: updateNode,
        addQuestion: addQuestion,
        updateQuestion: updateQuestion,
        updateCurrentSurvey: updateCurrentSurvey,
        addNode: addNode,
        deleteNode: deleteNode,
        deleteLogic: deleteLogic},
        dispatch)
}

// <button onClick={this.props.deleteNode.bind(null, this.props.id)}>delete</button>
// <button onClick={this.addSubSurvey}>Add Subsurvey</button>

export default connect(mapStateToProps, matchDispatchToProps)(Node);

// export default Node;

