// import React from 'react';
// import { orm } from './../redux/models.babel.js';
// import { bindActionCreators } from 'redux';
// import { connect } from 'react-redux';
// import { subSurveySelector } from './../redux/selectors.babel.js';
// import BucketsList from './BucketsList.babel.js';
// import { deleteSurvey, addBucket, deleteBucket, deleteAllBuckets, updateCurrentSurvey } from './../redux/actions.babel.js';


// class SubSurveyListItem extends React.Component {

// 	// PROPS RECEIVED:
// 	// parentQuestion={self.props.node_id}
//     // key={sub_survey.id}
//     // sub_survey_id={sub_survey.id}
//     // type_constraint={self.props.type_constraint}
//     // choices={self.props.choices}

//     // sub_survey
//     // buckets

// 	constructor(props) {
// 		super(props); 

// 		this.addBucketHandler = this.addBucketHandler.bind(this);
// 		this.listChoices = this.listChoices.bind(this);
// 		// this.listBuckets = this.listBuckets.bind(this);
// 	}

// 	// let bucketInput = null;
// 	// const parentQuestionTitle = props.parentQuestionTitle;
// 	componentWillReceiveProps(nextProps) {
// 		if (this.props.type_constraint!==nextProps.type_constraint) {
// 			this.props.deleteAllBuckets(this.props.sub_survey_id);
// 		};
// 		if (nextProps.type_constraint==='multiple_choice' &&
// 			this.props.type_constraint==='multiple_choice' &&
// 			nextProps.choices.length < this.props.choices.length) {
// 			this.props.deleteAllBuckets(this.props.sub_survey_id);
// 		};
// 	}


// 	addBucketHandler() {
// 		// let newList = [];
// 		// console.log('bucket handler', this.props, this.state.selected)

// 		// let bucketList = [].concat(this.props.sub_survey.buckets)
// 		let newBucket = {
// 			survey: this.props.sub_survey_id, 
// 			bucket_type: this.props.type_constraint, 
// 			bucket: undefined
// 		};
// 		if (this.props.type_constraint==='multiple_choice') {
// 			newBucket.bucket = {};
// 			newBucket.bucket.choice_number = parseInt(this.bucketInput.value);
// 			newBucket.id = parseInt(this.bucketInput.value);
// 		} else {
// 			newBucket.bucket = "[" + this.bucketInput.value + "]";
// 		}

// 		console.log('new bucket', newBucket.bucket);
// 		this.bucketInput.value = "";
// 		this.props.addBucket(newBucket);
// 	}


// 	listChoices() {
// 		console.log('item', this.props)
// 		let choiceList= [<option></option>];
// 		let mappedChoices = []
// 		if (this.props.choices) {
// 			mappedChoices = this.props.choices.map(function(choice, index) {
// 				if (choice.choice_text===undefined) return
// 				return(
// 					<option value={index}>{choice.choice_text.English}</option>
// 				)
// 			})
// 		}
// 		console.log('before rendering choices', choiceList);
// 		return choiceList.concat(mappedChoices);
// 	}

// 	render() {
// 		console.log('this props', this.props);
// 		const parentQuestionTitle = this.props.parentQuestionTitle;
// 		return (
//             <div>
//             	<span className="parent-question">
// 	            	{(this.props.parentQuestionTitle) &&
// 	            		this.props.parentQuestionTitle
// 	            	}
// 	            </span>
//             	<div>
// 	            	<button className="view-sub-survey-btn" onClick={this.props.updateCurrentSurvey.bind(null, this.props.sub_survey.id)}>View Sub-Survey</button>
// 	            	<button style={{float: "right"}} onClick={this.props.deleteSurvey.bind(null, this.props.sub_survey_id)}>Delete Sub-Survey</button>
//             	</div>
//             	<div style={{clear: "both"}}>
// 	            	<div style={{width: "50%", display: "inline-block", verticalAlign: "top", padding: "0px 20px", float: "none"}}>
// 	            		<label className="col-form-label">Bucket(s):</label>
// 	            		<div style={{border: "solid 1px black", height: "90px", overflowY: "scroll"}}>
	            			
// 	            			<BucketsList 
// 	            				buckets={this.props.buckets}
// 	            				type_constraint={this.props.type_constraint}
// 	            				deleteBucket={this.props.deleteBucket}
// 	            			/>
	            			
// 	            		</div>
// 		            </div>
// 		            <div style={{width: "50%", display: "inline-block", verticalAlign: "top", padding: "0px 20px", float: "none"}}>
// 		            	<label className="col-form-label">Add Bucket:</label>
// 			            <div>
// 			            	{(this.props.type_constraint=="multiple_choice") &&
// 				            	<select ref={(input) => { this.bucketInput = input; }} onChange={this.addBucketHandler}>
// 				            		{this.listChoices()}
// 				            	</select>
// 			            	}
// 			            	{(this.props.type_constraint!=="multiple_choice") &&
// 				            	<div>
// 				            		<input ref={(input) => { this.bucketInput = input; }}></input>
// 				            		<button onClick={this.addBucketHandler}>add bucket</button>
// 				            	</div>
// 			            	}
// 			            </div>
// 			        </div>
// 			    </div>
//             </div>
// 		)
// 	 }
// }


// function mapStateToProps(state, ownProps){
// 	const session = orm.session(state.orm);
// 	console.log('ownProps', ownProps)

// 	console.log('state dot orm', session)
// 	console.log(session.Survey)
// 	const id = ownProps.sub_survey_id

// 	const survey = session.Survey.withId(id).ref;

// 	let parentQuestionTitle = session.Question.withId(ownProps.parentQuestion).ref.title;

// 	console.log('the question title', parentQuestionTitle)

// 	parentQuestionTitle = parentQuestionTitle ? parentQuestionTitle.English : "this question is not yet defined!";

//     let surveyBuckets;
//     if (session.Survey.withId(id).buckets) surveyBuckets = session.Survey.withId(id).buckets.toRefArray();
//     else surveyBuckets = [];

//     return {
//     	sub_survey: survey,
//     	buckets: surveyBuckets,
//     	parentQuestionTitle: parentQuestionTitle
//     };
// }


// function matchDispatchToProps(dispatch){
//     return bindActionCreators({
//     						addBucket: addBucket,
//     						deleteBucket: deleteBucket,
//     						deleteSurvey: deleteSurvey,
//     						deleteAllBuckets: deleteAllBuckets,
//     						updateCurrentSurvey: updateCurrentSurvey}, dispatch);
// }


// export default connect(mapStateToProps, matchDispatchToProps)(SubSurveyListItem);
