import utils from './../utils.js';
import MultipleChoice from './MultipleChoice.babel.js';
import { Title, FacilityLogic, MinMaxLogic } from './Bucket.babel.js';

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
        this.listTitles = this.listTitles.bind(this);
        this.saveNode = this.saveNode.bind(this);

        this.state = {
            title: {},
            hint: {},
            type_constraint: '',
            choices: [],
            logic: {},
            saved: false
        }
    }

    componentWillReceiveProps(nextProps) {
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


    updateTitle(language, event) {
        console.log(event);
        let prevTitle = this.getTitleOrHintValue('title');
        //check if title input is the same as props title
        if (event.target.value===prevTitle) return;
        //check if title input is the same as current state title
        if (event.target.value===this.state.title) return;
        
        let prevTitleObj = {};
        let newTitle = {};
        newTitle[language] = event.target.value;
        
        let titleObj = Object.assign({}, this.state.title, newTitle);
        this.setState({title: titleObj}, function() {
            console.log('updated title', this.state.title);
            // let properties = this.state.title;
            // this.saveNode();
        });
    }


    updateHint(event) {
        let prevHint = this.getTitleOrHintValue('hint');
        // check if title input is the same as props title
        if (event.target.value===prevHint) return;
        // check if title input is the same as current state title
        if (event.target.value===this.state.title) return;

        let hintObj = {};
        hintObj[this.props.default_language] = event.target.value;
        this.setState({hint: hintObj}, function() {
            console.log('updated hint', this.state.hint);
            let properties = this.state.hint;
        });
    }


    listTitles(){
        const self = this;
        let displayTitle;
        return this.props.languages.map(function(language){
            console.log('language', language);
            displayTitle = self.getTitleOrHintValue('title', language);
            return (
                <Title
                    key={language.toString()}
                    language={language}
                    displayTitle={displayTitle}
                    updateTitle={self.updateTitle.bind(null, language)}
                />
            )
        }) 
    }


    addTypeConstraint(event) {
        console.log('being called.....')
        this.setState({type_constraint: event}, function(){
            console.log(this.state)
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
        delete node.saved;
        if (node.choices && (node.choices.length<1)) delete node.choices;
        if (JSON.stringify(node)===JSON.stringify(this.props.data.node)) {
            console.log('the node was not saved');
            return;
        }
        let updatedNode = Object.assign(this.props.data, node);
        console.log('the node was saved', updatedNode);
        this.props.updateNode(updatedNode);
    }


    render() {
        let displayHint = this.getTitleOrHintValue('hint');
        console.log('rendering node!', this.props.index)
        console.log('state', this.state)

        return (
            <div className="node">
                {this.listTitles()}
                <div className="form-group row">
                    <label htmlFor="question-hint" className="col-xs-2 col-form-label">Hint:</label>
                    <textarea className="form-control survey-title" rows="1" displayTitle={displayHint}
                    onBlur={this.updateHint}/>
                </div>
                <div className="form-group row">
                    <TypeConstraint 
                        addTypeConstraint={this.addTypeConstraint} 
                        saved={this.state.saved}/>
                </div>

                {(this.state.type_constraint==="multiple_choice") &&
                    <MultipleChoice
                        choices={this.state.choices}
                        addChoices={this.addChoices}
                        default_language={this.props.default_language}
                    />
                }

                {(this.state.type_constraint==="facility") &&
                    <FacilityLogic updateLogic={this.updateLogic}/>
                }

                {(this.state.type_constraint==="decimal") &&
                    <MinMaxLogic updateLogic={this.updateLogic}/>
                }

                <button onClick={this.props.deleteQuestion}>delete</button>
                <button onClick={this.saveNode}>save</button>
            </div>
        );
    }
}


function TypeConstraint(props) {

    let type_constraint = "text";

    function updateTypeConstraint(event) {
        type_constraint = event.target.value;
        props.addTypeConstraint(type_constraint)
        console.log('new type constraint', type_constraint);
    }

    function renderList() {
        return (
            <div>
                <label htmlFor="type-constraint" className="col-xs-2 col-form-label">Question Type:</label>
                <div className="col-xs-4">
                    <select className="form-control type-constraint"
                        onChange={updateTypeConstraint}>
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

    return (
        <div>
            {renderList()}
        </div>
    )
}

export default Node;