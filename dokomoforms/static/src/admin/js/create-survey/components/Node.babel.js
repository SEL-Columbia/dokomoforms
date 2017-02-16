import utils from './../utils.js';
import MultipleChoice from './MultipleChoice.babel.js';
import Logic from './Logic.babel.js';
import Fields from './Fields.babel.js';
import SubSurveyList from './SubSurveyList.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {nodeSelector} from './../redux/selectors.babel.js';
import {addSurvey, addNode, updateNode, addQuestion, updateQuestion, updateCurrentSurvey, deleteNode} from './../redux/actions.babel.js';

class Node extends React.Component {

    constructor(props) {
        super(props);

        this.getTitleOrHintValue = this.getTitleOrHintValue.bind(this);
        this.updateTitle = this.updateTitle.bind(this);
        this.updateHint = this.updateHint.bind(this);
        this.addTypeConstraint = this.addTypeConstraint.bind(this);
        this.addAllowMultiple = this.addAllowMultiple.bind(this);
        this.addChoices = this.addChoices.bind(this);
        this.updateChoices = this.updateChoices.bind(this);
        this.addSubSurvey = this.addSubSurvey.bind(this);
        this.showSubSurveys = this.showSubSurveys.bind(this);
        this.listTitles = this.listTitles.bind(this);
        this.allowOther = this.allowOther.bind(this);
        this.updateNumber = this.updateNumber.bind(this);
        // this.toggleField = this.toggleField.bind(this);

        this.state = {
            title: {},
            showHint: false,
            showLogic: false,
            allow_multiple: false,
            allow_other: false,
            type_constraint: 'text',
            choices: [],
            sub_surveys: [],
            logic: {},
            saved: false,
            showSubSurveys: false,
        }
    }

    componentWillReceiveProps(nextProps) {
        if (!this.props.repeatable) return;
        if (this.props.repeatable=="true") this.props.updateNode({id: this.props.id, repeatable: "true"})
        if (this.props.repeatable=="false") this.props.updateNode({id: this.props.id, repeatable: "false"})
    }

    getTitleOrHintValue(property, language) {
        if (!this.props.data ||
            !this.props.data[property]) return '';
        else return this.props.data[property][language]
    };

    updateChoices(choiceList){
        console.log('updated node', choiceList)
        const updatedNode = Object.assign(this.props.data, {choices: choiceList});
        this.props.updateNode({id: this.props.id, question: updatedNode});

        // this.setState({choices: choiceList}, function(){
        //     this.props.updateNode(this.props.node.id, {choices: this.state.choices});
        // })
    }


    updateTitle(property, event) {
        console.log('title', event.target.value);
        const question = this.props.data;
        const titleObj = {type_constraint: this.state.type_constraint, title: {English: event.target.value}};
        const updatedQuestion = Object.assign(question, titleObj);
        // this.props.updateNode({id: this.props.id, node: updatedNode});

        const newQuestion = {id: this.props.id, question: updatedQuestion};

        this.props.updateQuestion(updatedQuestion);
    }


    updateHint(property, event) {
        const hintObj = {hint: {English: event.target.value}};
        const node = this.props.data;
        const updatedQuestion = Object.assign(node, hintObj);
        this.props.updateQuestion(updatedQuestion);
        // let prevHint = this.getTitleOrHintValue('hint');
        // // check if title input is the same as props title
        // if (event.target.value===prevHint) return;
        // // check if title input is the same as current state title
        // if (event.target.value===this.state.title) return;

        // let newHint = {};
        // newHint[language] = event.target.value;
        
        // let hintObj = Object.assign({}, this.state.hint, newHint);
        // this.setState({hint: hintObj}, function() {
        //     console.log('updated hint', this.state.hint);
        //     // let properties = this.state.title;
        //     this.saveNode();
        // });
    }

    showSubSurveys(){
        this.setState({showSubSurveys: true})
    }

    addSubSurvey() {
        const nodeId = utils.addId('node');
        const surveyId = utils.addId('survey');
        const newSubSurvey = {
            id: surveyId, 
            node: this.props.id
        };
        const newQuestion = {
            id: nodeId
        };
        const newNode = {
            id: nodeId,
            question: nodeId,
            survey: newSubSurvey.id
        };
        console.log('ss from node')
        this.props.addSurvey(newSubSurvey);
        this.props.addQuestion(newQuestion);
        this.props.addNode(newNode);
        // this.props.addSurveyToNode(newSubSurvey);
        // this.props.addNode(newNode);
        // let sub_surveys = [];
        // if (this.props.sub_surveys) {
        //     sub_surveys = sub_surveys.concat(this.props.sub_surveys)
        // }
        // let newSurvey = {
        //     id: utils.addId('survey'),
        //     nodes: [],
        //     node: this.props.id
        // }
        // sub_surveys.push(newSurvey.id)
        // this.props.addSurveyToNode(newSurvey)
    }


    listTitles(){

        const self = this;
        let displayQuestion, displayHint, key;

        return this.props.languages.map(function(language){
            console.log('language', language);
            displayQuestion = self.getTitleOrHintValue('title', language);
            displayHint = self.getTitleOrHintValue('hint', language);
            console.log('display', displayQuestion, displayHint)
            key = language.toString()
            return (
                <div key={language} className="title-group">
                    <span className="language-header">{language}</span>
                        <Title
                            property={'Question'}
                            key={key+"_t"}
                            language={language}
                            display={displayQuestion}
                            update={self.updateTitle.bind(null, language)}
                        />

                    {(self.state.showHint || self.props.data.hint) &&
                        <Title
                            property={'Hint'}
                            key={key+"_h"}
                            language={language}
                            display={displayHint}
                            update={self.updateHint.bind(null, language)}
                        />
                    }
                </div>
            )
        }) 
    }


    addTypeConstraint(value) {
        const node = this.props.data;
        const updatedQuestion = Object.assign(node, {type_constraint: value});
        // console.log('updated node', updatedNode, this.props)
        this.props.updateQuestion(updatedQuestion);
        this.setState({type_constraint: value});
        // this.props.updateNode(this.props.id, {type_constraint: event.target.value})
    }

    updateNumber(event) {
        const node = this.props.data;
        console.log('updating number', event.target.value)
        const updatedQuestion = Object.assign(node, {number: event.target.value});
        // console.log('updated node', updatedNode, this.props)
        this.props.updateQuestion(updatedQuestion);
    }

    addAllowMultiple(event) {
        let value = event.target.value;
        this.setState({allow_multiple: value}, function(){
            const updatedQuestion = Object.assign(this.props.data, {allow_multiple: value});
            this.props.updateQuestion(updatedQuestion)
        })
    }

    allowOther(bool) {
        const nodeObj = Object.assign(this.props.data, {allow_other: bool});
        this.props.updateNode({id: this.props.node.id, question: nodeObj})
        // this.setState({allow_other: bool}, function(){
        //     console.log('allow other', bool, this.state)
        //     this.saveNode();
        // })
    }


    addChoices(choiceList){
        this.setState({choices: choiceList}, function(){
            this.props.updateNode(this.props.node.id, {choices: this.state.choices});
        })
    }

    // toggleField(field){
    //     console.log('togglefield', field, this.state[field])
    //     this.setState({[field]: !this.state[field]})
    // }


    render() {
        let displayTitle = this.getTitleOrHintValue('title');
        let displayHint = this.getTitleOrHintValue('hint');
        console.log('state', this.state)
        console.log('node props', this.props)

        const number = (this.props.data.number) ? this.props.data.number: "";

        return (
            <div className="node">
                Number: <input style={{width: "80px"}} onBlur={this.updateNumber} placeholder={number}></input>
                {this.listTitles()}
                <div className="form-group row">
                    <TypeConstraint 
                        type_constraint={this.props.data.type_constraint}
                        addTypeConstraint={this.addTypeConstraint} 
                        saved={this.state.saved}/>
                    <div>
                        <label htmlFor="type-constraint" className="col-xs-2 col-form-label">Allow Multiple Responses:</label>
                        <div className="col-xs-4">
                            <select className="form-control type-constraint"
                                value={this.props.data.allow_multiple || this.state.allow_multiple}
                                onChange={this.addAllowMultiple}>
                                <option></option>
                                <option value={false}>no</option>
                                <option value={true}>yes</option>
                            </select>
                        </div>
                    </div>
                </div>

                {(this.state.type_constraint=="multiple_choice" ||
                    this.props.data.type_constraint=="multiple_choice") &&
                    <MultipleChoice
                        questionId={this.props.data.id}
                        addChoices={this.addChoices}
                        updateChoices={this.updateChoices}
                        allowOther={this.allowOther}
                        default_language={this.props.default_language}
                    />
                }

                {(this.props.sub_surveys && this.props.sub_surveys.length > 0) &&
                    <SubSurveyList
                        type_constraint={this.props.data.type_constraint || this.state.type_constraint}
                        sub_surveys={this.props.sub_surveys}
                        choices={this.props.data.choices}
                        id={this.props.id}
                        addSubSurvey={this.addSubSurvey}
                        goToSubSurvey={this.goToSubSurvey}
                    />
                }

                <Logic type_constraint={this.state.type_constraint} id={this.props.id}/>

                <button onClick={this.props.deleteNode.bind(null, this.props.id)}>delete</button>
                <button onClick={this.addSubSurvey}>Add Subsurvey</button>
                <div className="form-group">
                    <Fields toggleField={(field => this.setState({[field]: !this.state[field]}))}/>
                </div>
            </div>
        );
    }
}


function Title(props) {
    console.log('title', props)
    return(
        <div className="title">
            <div className="form-group row">
                <label htmlFor="question-title" className="col-xs-4 col-form-label">{props.property}</label>
            </div>
            <div className="form-group row col-xs-12">
                <textarea className="form-control question-title" rows="1" placeholder={props.display}
                    onBlur={props.update.bind(props.property)}/>
            </div>
        </div>
    )
}


class TypeConstraint extends React.Component {

    constructor(props) {
        super(props)

        this.updateTypeConstraint = this.updateTypeConstraint.bind(this);
        this.renderList = this.renderList.bind(this);

        this.state = {
            type_constraint: "text"
        }
    }

    componentWillMount(){
        console.log('type onstraint monti')
        if (!this.props.type_constraint || !this.props.type_constraint.length) {
            return;
        }
        this.setState({type_constraint: this.props.type_constraint})
    }


    updateTypeConstraint(event) {
        this.setState({type_constraint: event.target.value}, function(){
            this.props.addTypeConstraint(this.state.type_constraint)
            console.log('new type constraint', this.state.type_constraint);
        })
    }

    renderList() {
        return (
            <div>
                <label htmlFor="type-constraint" className="col-xs-2 col-form-label">Question Type:</label>
                <div className="col-xs-4">
                    <select className="form-control type-constraint"
                        value={this.state.type_constraint}
                        onChange={this.updateTypeConstraint}>
                    <option></option>
                    <option value="text">text</option>
                    <option value="photo">photo</option>
                    <option value="integer">integer</option>
                    <option value="decimal">decimal</option>
                    <option value="date">date</option>
                    <option value="time">time</option>
                    <option value="timestamp">timestamp</option>
                    <option value="location">location</option>
                    <option value="facility">facility</option>
                    <option value="multiple_choice">multiple choice</option>
                    <option value="note">note</option>
                    </select>
                </div>
            </div>
        )
    }

    render() {
        return (
            <div>
                {this.renderList()}
            </div>
        )
    }
}


function mapStateToProps(state){
    console.log('here', this.props);
    console.log(state);
    return {};
}


function matchDispatchToProps(dispatch){
    return bindActionCreators({
        addSurvey: addSurvey,
        updateNode: updateNode,
        addQuestion: addQuestion,
        updateQuestion: updateQuestion,
        updateCurrentSurvey: updateCurrentSurvey,
        addNode: addNode,
        deleteNode: deleteNode},
        dispatch)
}


export default connect(mapStateToProps, matchDispatchToProps)(Node);

// export default Node;