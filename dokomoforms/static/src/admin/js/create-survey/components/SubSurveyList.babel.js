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
    		subList.forEach(function(sub) {
		        sub_survey = sub
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

class SubSurveyListItem extends React.Component {

	constructor(props) {
		super(props)

		this.viewSubSurveyHandler = this.viewSubSurveyHandler.bind(this)
		this.addBucketHandler = this.addBucketHandler.bind(this)
		this.listChoices = this.listChoices.bind(this)
		this.listBuckets = this.listBuckets.bind(this)
		this.updateSelected = this.updateSelected.bind(this)

		this.state = {
			selected: null
		}
	}

	viewSubSurveyHandler() {
		this.props.goToSubSurvey(this.props.sub_survey.id)
	}

	addBucketHandler(){
		console.log('refs!', this.refs)
		console.log('bucket handler', this.props, this.state.selected)

		let bucketList = [].concat(this.props.sub_survey.buckets)
		let newBucket = {bucket_type: this.props.type_constraint, bucket: undefined}
		if (this.props.type_constraint=='multiple_choice') {
			newBucket.bucket = {}
			newBucket.bucket.choice_number = parseInt(this.state.selected);
		} else {
			newBucket.bucket = "[" + this.state.selected + "]";
		}

		console.log('new bucket', newBucket.bucket);
		bucketList.push(newBucket)
		this.props.addBucket({buckets: bucketList}, this.props.sub_survey.id)
	}

	updateSelected(event){
		this.setState({selected: event.target.value})
	}

	listChoices() {
		console.log('item', this.props)
		let choiceList= [<option></option>];
		let mappedChoices = []
		if (this.props.choices) {
			mappedChoices = this.props.choices.map(function(choice, index) {
				console.log(choice.English);
				return(
					<option value={index}>{choice.English}</option>
				)
			})
		}
		return choiceList.concat(mappedChoices);
	}

	listBuckets() {
		let buckets = [].concat(this.props.sub_survey.buckets)
		return buckets.map(function(bucket) {
			return(JSON.stringify(bucket))
		})
	}

	render() {
		console.log(this.props.sub_survey)
		return (
            <div>
            	<div>
	            	<button onClick={this.viewSubSurveyHandler} disabled={!this.props.sub_survey.buckets.length}>SubSurvey</button>
            	</div>
            	<div>
	            	<label htmlFor="type-constraint" className="col-xs-2 col-form-label">Bucket(s):</label>
	            	{this.listBuckets()}
	            </div>
	            <div>
	            	<label htmlFor="type-constraint" className="col-xs-2 col-form-label">Add Bucket:</label>
		            <div className="col-xs-4">
		            	{(this.props.type_constraint=="multiple_choice") &&
			            	<select onChange={this.updateSelected} value={this.props.sub}>
			            		{this.listChoices()}
			            	</select>
		            	}
		            	{(this.props.type_constraint!=="multiple_choice") &&
		            		<input onBlur={this.updateSelected}></input>
		            	}
		            </div>
		            <button onClick={this.addBucketHandler}>add bucket</button>
		        </div>
            </div>
		)
	}
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