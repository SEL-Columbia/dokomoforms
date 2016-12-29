import utils from './../utils.js';
import MultipleChoice from './MultipleChoice.babel.js';
import { Title, FacilityLogic, MinMaxLogic } from './Logic.babel.js';
import SubSurveyList from './SubSurveyList.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {addSurvey, updateNode, updateSurveyView} from './../redux/actions.babel.js';

class Node extends React.Component {

    // Node is currently referring to the full node object that contains the question
    // and the associated sub-surveys

    constructor(props) {
        super(props);

        this.getTitleOrHintValue = this.getTitleOrHintValue.bind(this);
        this.updateTitle = this.updateTitle.bind(this);
        this.updateHint = this.updateHint.bind(this);
        this.addTypeConstraint = this.addTypeConstraint.bind(this);
        this.addChoices = this.addChoices.bind(this);
        this.updateLogic = this.updateLogic.bind(this);
        this.updateChoices = this.updateChoices.bind(this);
        this.addSubSurvey = this.addSubSurvey.bind(this);
        this.showSubSurveys = this.showSubSurveys.bind(this);
        this.goToSubSurvey = this.goToSubSurvey.bind(this);
        this.listTitles = this.listTitles.bind(this);
        this.saveNode = this.saveNode.bind(this);
        this.addSubSurveyHandler = this.addSubSurveyHandler.bind(this);

        this.state = {
            title: {},
            hint: {},
            type_constraint: '',
            choices: [],
            sub_surveys: [],
            logic: {},
            saved: false,
            showSubSurveys: false
        }
    }

    componentWillReceiveProps(nextProps) {
        console.log('will receive props');
        console.log(nextProps);
        if (nextProps.sub_surveys && nextProps.sub_surveys.length) {
            this.setState({showSubSurveys: true})
        }
        // if (nextProps.saved===true) {
        //     console.log('true')
        //     this.setState({editable: false}, function(){
        //         this.save()
        //     })
        // };
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (JSON.stringify(this.props)===JSON.stringify(nextProps)
            && JSON.stringify(this.state)===JSON.stringify(nextState)) return false;
        else {
            console.log('props did change', this.props, nextProps);
            return true;
        }
    }

    getTitleOrHintValue(property, language) {
        if (!this.props.data ||
            !this.props.data[property]) return '';
        else return this.props.data[property][language]
    };

    updateChoices(choiceList){
        let newChoices = [];
        if (this.state.type_constraint=='multiple_choice') {
            newChoices = newChoices.concat(choiceList)
        }
        this.setState({choices: choiceList}, function(){
            this.saveNode()
        })
    }


    updateTitle(language, event) {
        console.log(event);
        let prevTitle = this.getTitleOrHintValue('title');
        //check if title input is the same as props title
        if (event.target.value===prevTitle) return;
        //check if title input is the same as current state title
        if (event.target.value===this.state.title) return;
        
        let newTitle = {};
        newTitle[language] = event.target.value;
        
        let titleObj = Object.assign({}, this.state.title, newTitle);
        this.setState({title: titleObj}, function() {
            console.log('updated title', this.state.title);
            // let properties = this.state.title;
            this.saveNode();
        });
    }


    updateHint(language, event) {
        let prevHint = this.getTitleOrHintValue('hint');
        // check if title input is the same as props title
        if (event.target.value===prevHint) return;
        // check if title input is the same as current state title
        if (event.target.value===this.state.title) return;

        let newHint = {};
        newHint[language] = event.target.value;
        
        let hintObj = Object.assign({}, this.state.hint, newHint);
        this.setState({hint: hintObj}, function() {
            console.log('updated hint', this.state.hint);
            // let properties = this.state.title;
            this.saveNode();
        });
    }

    addSubSurveyHandler(){
        console.log('add subsurvey being called');
        if (this.state.showSubSurveys) {
            this.addSubSurvey();
        }
        this.showSubSurveys();
    }

    showSubSurveys(){
        this.setState({showSubSurveys: true})
    }

    addSubSurvey() {
        let sub_surveys = [];
        if (this.props.sub_surveys) {
            sub_surveys = sub_surveys.concat(this.props.sub_surveys)
        }
        let newSurvey = {
            id: utils.addId('survey'),
            buckets: [],
            nodes: []
        }
        sub_surveys.push(newSurvey.id)
        console.log('trying to add subsurbeys!!!!!')
        this.props.addSurvey(newSurvey, newSurvey.id);
        console.log(this.props.id, sub_surveys)
        this.props.updateNode(this.props.id, sub_surveys, 'sub_surveys')
    }

    goToSubSurvey(id) {
        console.log('before reducer', this.props.id)
        this.props.updateSurveyView(this.props.id, id, this.props.parent)
        // let copy = [];
        // copy = copy.concat(this.state.sub_surveys)
        // let newSubSurvey = {
        //     id: utils.addId('survey'),
        //     buckets: [{
        //         bucket_type: this.state.type_constraint,
        //         buckets: [bucket]
        //     }],
        //     nodes: []
        // }
        // copy.push(newSubSurvey);
        // this.setState({sub_surveys: copy}, function(){
        //     console.log('added sub to node', this.state)
        //     this.saveNode();
        //     this.props.showSubSurvey(newSubSurvey, this.state.title)
        // })
    }


    listTitles(){

        const self = this;
        let displayQuestion, displayHint, key;

        return this.props.languages.map(function(language){
            console.log('language', language);
            displayQuestion = self.getTitleOrHintValue('title', language);
            displayHint = self.getTitleOrHintValue('hint', language);
            console.log('display!!!', displayQuestion, displayHint)
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


    addTypeConstraint(event) {
        console.log('being called.....')
        this.setState({type_constraint: event}, function(){
            console.log(this.state)
            this.saveNode()
        })
    }


    updateLogic(logic) {
        this.setState({logic: logic});
    }

    addChoices(choiceList){
        this.setState({saved: choiceList})
    }


    saveNode() {
        console.log('saved')
        this.setState({saved: true})
        let node = this.state;
        node.languages = this.props.languages;
        delete node.saved;
        delete node.showSubSurveys;
        if (node.choices && node.choices.length<1) delete node.choices;
        if (JSON.stringify(node)===JSON.stringify(this.props.data.node)) {
            console.log('the node was not saved');
            return;
        }
        let updatedNode = Object.assign(this.props.data, node);
        console.log('the node was saved', updatedNode);
        this.props.updateNodeOther(updatedNode);
    }


    render() {
        let displayTitle = this.getTitleOrHintValue('title');
        let displayHint = this.getTitleOrHintValue('hint');
        console.log('rendering node!', this.props.index)
        console.log('state', this.state)
        console.log('props???', this.props)

        return (
            <div className="node">
                {this.listTitles()}
                <div className="form-group row">
                    <TypeConstraint 
                        type_constraint={this.props.data.type_constraint}
                        addTypeConstraint={this.addTypeConstraint} 
                        saved={this.state.saved}/>
                        <div>
                    <label htmlFor="type-constraint" className="col-xs-2 col-form-label">Allow Multiple Responses:</label>
                    <div className="col-xs-4">
                        <select className="form-control type-constraint">
                            <option value="photo">no</option>
                            <option value="text">yes</option>
                        </select>
                    </div>
                </div>
            </div>

                {(this.state.type_constraint=="multiple_choice" ||
                    this.props.data.type_constraint=="multiple_choice") &&
                    <MultipleChoice
                        choices={this.props.data.choices}
                        addChoices={this.addChoices}
                        updateChoices={this.updateChoices}
                        default_language={this.props.default_language}
                    />
                }

                {(this.state.showSubSurveys===true || this.props.sub_surveys) &&
                    <SubSurveyList
                        type_constraint={this.props.data.type_constraint}
                        sub_surveys={this.props.sub_surveys}
                        choices={this.props.data.choices}
                        id={this.props.id}
                        addSubSurvey={this.addSubSurvey}
                        goToSubSurvey={this.goToSubSurvey}
                    />
                }

                <button onClick={this.props.deleteQuestion}>delete</button>
                <button onClick={this.saveNode}>save</button>
                <button onClick={this.addSubSurveyHandler}>Add Subsurvey</button>
            </div>
        );
    }
}


class TypeConstraint extends React.Component {

    constructor(props) {
        super(props)

        this.updateTypeConstraint = this.updateTypeConstraint.bind(this)
        this.renderList = this.renderList.bind(this);

        this.state = {
            type_constraint: "text"
        };
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
    console.log('here')
    console.log(state)
    return {
        surveys: state.surveys,
        nodes: state.nodes
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({addSurvey: addSurvey, updateNode: updateNode, updateSurveyView: updateSurveyView}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(Node);

// export default Node;