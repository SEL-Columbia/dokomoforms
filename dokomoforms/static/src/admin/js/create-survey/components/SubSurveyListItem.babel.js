import React from 'react';
import utils from './../utils.js';
import { orm } from './../redux/models.babel.js';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { subSurveySelector } from './../redux/selectors.babel.js';
import BucketsList from './BucketsList.babel.js';
import { deleteSurvey, addBucket, deleteBucket, deleteAllBuckets, updateCurrentSurvey } from './../redux/actions.babel.js';


class SubSurveyListItem extends React.Component {

	// PROPS RECEIVED:
	// parentQuestion={self.props.node_id}
    // key={sub_survey.id}
    // sub_survey_id={sub_survey.id}
    // type_constraint={self.props.type_constraint}
    // choices={self.props.choices}

    // sub_survey
    // buckets

	constructor(props) {
		super(props); 

		this.addBucketHandler = this.addBucketHandler.bind(this);
		this.listChoices = this.listChoices.bind(this);
		// this.listBuckets = this.listBuckets.bind(this);
	}

	// let bucketInput = null;
	// const parentQuestionTitle = props.parentQuestionTitle;
	componentWillReceiveProps(nextProps) {
		console.log('new props', nextProps, this.props)
		if (this.props.type_constraint!==nextProps.type_constraint) {
			console.log('the type constraint changed');
			this.props.deleteAllBuckets(this.props.sub_survey_id);
		};
		if (nextProps.type_constraint==='multiple_choice' &&
			this.props.type_constraint==='multiple_choice' &&
			nextProps.choices.length < this.props.choices.length) {
			this.props.deleteAllBuckets(this.props.sub_survey_id);
		}
	}


	addBucketHandler() {
		// let newList = [];
		// console.log('bucket handler', this.props, this.state.selected)

		// let bucketList = [].concat(this.props.sub_survey.buckets)
		let newBucket = {
			survey: this.props.sub_survey_id, 
			bucket_type: this.props.type_constraint, 
			bucket: undefined,
		};
		if (this.props.type_constraint==='multiple_choice') {
			newBucket.bucket = {};
			newBucket.id = parseInt(this.bucketInput.value);

			console.log('before it', this.props.choices, this.bucketInput.value)

			for (var i=0; i<this.props.choices.length; i++) {
				if (this.props.choices[i].id===newBucket.id) {
					console.log('found it', this.props.choices[i], newBucket.id);
					newBucket.bucket.choice_number = parseInt(i);
					break;
				}
			}

			// newBucket.bucket.choice_number = parseInt(this.bucketInput.value);
			newBucket.id = parseInt(this.bucketInput.value);
			this.bucketInput.value = "";
		} else {
			const min = this.bucketMin.value || "0";
			const max = this.bucketMax.value || "100";
			newBucket.bucket = "[" + min + "," + max + "]";
			newBucket.id = utils.addId('bucket');
			this.bucketMin.value = "";
			this.bucketMax.value = "";
		}

		console.log('new bucket', newBucket.bucket);
		this.props.addBucket(newBucket);
	}


	listChoices() {
		let choiceList = [<option></option>];
		let choice_text;

		self = this;
		let mappedChoices = [];
		if (self.props.choices) {
			mappedChoices = self.props.choices.map(function(choice, index) {
				console.log('choice', choice, index);
				choice_text = choice.choice_text[self.props.default_language];
				if (choice_text===undefined) return;
				return(
					<option value={choice.id}>{choice_text}</option>
				)
			})
		}
		console.log('before rendering choices', choiceList);
		return choiceList.concat(mappedChoices);
	}

	render() {
		console.log('SS list item props', this.props.type_constraint);
		const parentQuestionTitle = this.props.parentQuestionTitle;
		return (
            <div>
            	<span className="parent-question">
	            	{(this.props.parentQuestionTitle) &&
	            		this.props.parentQuestionTitle
	            	}
	            </span>
            	<div>
	            	<button className="view-sub-survey-btn" onClick={this.props.updateCurrentSurvey.bind(null, this.props.sub_survey.id)}>View Sub-Survey</button>
	            	<button style={{float: "right"}} onClick={this.props.deleteSurvey.bind(null, this.props.sub_survey_id)}>Delete Sub-Survey</button>
            	</div>
            	<div style={{clear: "both"}}>
	            	<div style={{width: "50%", display: "inline-block", verticalAlign: "top", padding: "0px 20px", float: "none"}}>
	            		<label className="col-form-label">Bucket(s):</label>
	            		<div style={{border: "solid 1px black", height: "90px", overflowY: "scroll"}}>
	            			
	            			<BucketsList
	            				choices={this.props.choices || undefined}
	            				buckets={this.props.buckets}
	            				type_constraint={this.props.type_constraint}
	            				default_language={this.props.default_language}
	            				deleteBucket={this.props.deleteBucket}
	            			/>
	            			
	            		</div>
		            </div>
		            <div style={{width: "50%", display: "inline-block", verticalAlign: "top", padding: "0px 20px", float: "none"}}>
		            	<label className="col-form-label">Add Bucket:</label>
			            <div>
			            	{(this.props.type_constraint=="multiple_choice") &&
				            	<select ref={(input) => { this.bucketInput = input; }} onChange={this.addBucketHandler}>
				            		{this.listChoices()}
				            	</select>
			            	}
			            	{(this.props.type_constraint!=="multiple_choice") &&
				            	<div>
				            		<label>Min:</label><input placeholder={"0"} className="min-max" ref={(min) => { this.bucketMin = min; }}></input>
				            		<label>Max:</label><input placeholder={"100"} className="min-max" ref={(max) => { this.bucketMax = max; }}></input>
				            		<button onClick={this.addBucketHandler}>add bucket</button>
				            	</div>
			            	}
			            </div>
			        </div>
			    </div>
            </div>
		)
	 }
}


function mapStateToProps(state, ownProps){
	const session = orm.session(state.orm);
	console.log('ownProps', ownProps)

	console.log('state dot orm', session)
	console.log(session.Survey)
	const id = ownProps.sub_survey_id

	const survey = session.Survey.withId(id).ref;

	let parentQuestionTitle = session.Question.withId(ownProps.parentQuestion).ref.title;

	console.log('the question title', parentQuestionTitle)

	parentQuestionTitle = parentQuestionTitle ? parentQuestionTitle[state.default_language] : "this question is not yet defined!";

    let surveyBuckets;
    if (session.Survey.withId(id).buckets) surveyBuckets = session.Survey.withId(id).buckets.toRefArray();
    else surveyBuckets = [];

    return {
    	sub_survey: survey,
    	buckets: surveyBuckets,
    	parentQuestionTitle: parentQuestionTitle,
    	default_language: state.default_language
    };
}


function matchDispatchToProps(dispatch){
    return bindActionCreators({
    						addBucket: addBucket,
    						deleteBucket: deleteBucket,
    						deleteSurvey: deleteSurvey,
    						deleteAllBuckets: deleteAllBuckets,
    						updateCurrentSurvey: updateCurrentSurvey}, dispatch);
}


export default connect(mapStateToProps, matchDispatchToProps)(SubSurveyListItem);
