
// export default function BucketsList(props) {
		
// 	// console.log('buckets', this.props.sub_survey)
// 	// let buckets = [];
// 	// if (this.props.sub_survey.list) buckets = buckets.concat(this.props.sub_survey.list)
// 	// if (this.props.sub_survey.buckets && this.props.sub_survey.buckets.length) {
// 	// 	console.log('buckets apparently');
// 	// 	buckets = [].concat(this.props.sub_survey.buckets)
// 	// }
// 	// if (this.state.buckets.length) {
// 	// 	buckets = buckets.concat(this.state.buckets)
// 	// }
// 	// let self = this;

// 	function listBuckets() {
// 		if (props.buckets.length < 1) return;
// 		const buckets = [].concat(props.buckets);
// 		console.log(buckets.length, buckets)

// 		console.log('type', props.type_constraint)
// 		let bucket;

// 		return buckets.map(function(bucket) {
// 			let bucketId = bucket.id;
// 			if (props.type_constraint==="multiple_choice") {
// 				console.log(props.choices)
// 				console.log(bucket.bucket.choice_number)
// 				bucket = props.choices[bucket.bucket.choice_number].choice_text.English;
// 			} else { 
// 				bucket = bucket.bucket
// 				console.log('bucket before', bucket)
// 				bucket = bucket.slice(0, -1);
// 				bucket = bucket.slice(1, bucket.length);
// 			}
// 			console.log('bucket after', bucket)
// 			return(
// 				<div key={bucket.id}>
// 					<div style={{height: "25px", paddingLeft: "10px"}}>
// 						<span>{bucket}</span>{(props.deleteBucket) && <button style={{float: "right", height: "25px"}} onClick={props.deleteBucket.bind(null, bucketId)}>x</button>}
// 					</div>
// 					<hr style={{margin: "0px", color: "red"}}/>
// 				</div>
// 			)
// 		})
// 	}

// 	return(
// 		<div>
// 			{listBuckets()}
// 		</div>
// 	)
// }
