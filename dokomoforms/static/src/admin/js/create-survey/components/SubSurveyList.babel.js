import utils from './../utils.js';
import SubSurvey from './SubSurvey.babel.js';
import MultipleChoice from './MultipleChoice.babel.js';
import { Title, FacilityLogic, MinMaxLogic } from './Logic.babel.js';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {updateSurveys, getSurvey} from './../redux/actions.babel.js';

class SubSurveyList extends React.Component {

	constructor(props) {
        super(props);

        this.addBucket = this.addBucket.bind(this);
        this.goToSubSurvey = this.goToSubSurvey.bind(this)
        this.listSubSurveys = this.listSubSurveys.bind(this)

        this.state = {}
    }

    componentWillMount() {
    	console.log('its mounting', this.props)
    	if (!this.props.sub_surveys || !this.props.sub_surveys.length) {
    		this.props.addSubSurvey()
    	}
    }

    addBucket(bucket, survey_id) {
    	this.props.updateSurveys(bucket, survey_id)
    	// let copy = [];
    	// copy = copy.concat(this.state.buckets)
    	// copy.push(event.target.value)
    	// console.log('new bucket', copy)
    }

    listSubSurveys(){
    	let self = this;
    	console.log('listSubSurveys')
    	let subList = [];
    	let renderList = [];
    	if (this.props.sub_surveys) {
    		console.log('it has subsurveys')
    		console.log(this.props)
    		subList = subList.concat(this.props.sub_surveys)
    	}
    	if (subList.length > 0) {
    		console.log('subList', subList)
    		let sub_survey;
    		subList.forEach(function(subId, index) {
		        sub_survey = self.props.surveys[subId]
		        console.log('sub_survey', sub_survey)
		        renderList.push(
		            <SubSurveyListItem
		            	goToSubSurvey={self.goToSubSurvey}
		            	key={sub_survey.id}
		                sub_survey={sub_survey}
		                type_constraint={self.props.type_constraint}
		                choices={self.props.choices}
		                addBucket={self.addBucket}
		            />
		        )
			})
    	}
    	console.log(renderList);
		return renderList;
    }

    goToSubSurvey(survey_id) {
    	console.log('props', this.props)
    	console.log('goto subsurvey', survey_id)
    	this.props.goToSubSurvey(survey_id)
    }

	render(){
		console.log('from subsurvey', this.props)
		return(
			<div>
				<span className="language-header">SubSurvey List</span>
				{this.listSubSurveys()}
			</div>
		)
	}
}

function SubSurveyListItem(props) {

	let type_constraint = props.type_constraint;

	function viewSubSurveyHandler(){
		props.goToSubSurvey(props.sub_survey.id)
	}

	function addBucketHandler(event){
		console.log('bucket handler', props, event.target.value)

		let newBucket = {bucket_type: props.type_constraint, bucket: undefined}
		if (props.type_constraint=='multiple_choice') {
			newBucket.bucket = {}
			newBucket.bucket.choice_number = parseInt(event.target.value);
		} else {
			newBucket.bucket = "[" + event.target.value + "]";
		}

		console.log('new bucket', newBucket.bucket);
		props.addBucket({buckets: [newBucket]}, props.sub_survey.id)
	}

	function listChoices() {
		console.log('item', props)
		let choiceList= [<option></option>];
		let mappedChoices = []
		if (props.choices) {
			mappedChoices = props.choices.map(function(choice, index) {
				console.log(choice.English);
				return(
					<option value={index}>{choice.English}</option>
				)
			})
		}
		return choiceList.concat(mappedChoices);
	}

	return (

		<div className="form-group row">
            <div>
	            <label htmlFor="type-constraint" className="col-xs-2 col-form-label">Bucket</label>
	            <div className="col-xs-4">
	            	{(props.type_constraint=="multiple_choice") &&
		            	<select onChange={addBucketHandler} value={props.sub}>
		            		{listChoices()}
		            	</select>
	            	}
	            	{(props.type_constraint!=="multiple_choice") &&
	            		<input onBlur={addBucketHandler}></input>
	            	}
	            </div>
            </div>
            <div>
	            <button onClick={viewSubSurveyHandler}>SubSurvey</button>
            </div>
        </div>
	)
}

function mapStateToProps(state){
    return {
        surveys: state.surveys
    }
}

function matchDispatchToProps(dispatch){
    return bindActionCreators({getSurvey: getSurvey, updateSurveys: updateSurveys}, dispatch)
}

export default connect(mapStateToProps, matchDispatchToProps)(SubSurveyList);