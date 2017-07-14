
export default function BucketsList(props) {

	function listBuckets() {
		if (props.buckets.length < 1) return;
		const buckets = [].concat(props.buckets);
		console.log(buckets.length, buckets)

		console.log('type', props.type_constraint)
		
		let bucket_list_item;
		return buckets.map(function(bucket) {
			if (props.type_constraint==="multiple_choice") {
				let choice = props.choices[bucket.bucket.choice_number];
				console.log('props choices', props.choices);
				console.log('choice num', bucket.bucket.choice_number);
				bucket_list_item = choice.choice_text[props.default_language];
				console.log('bucket_list_item', bucket_list_item);
			} else { 
				bucket_list_item = bucket.bucket;
				console.log('bucket before', bucket_list_item);
				bucket_list_item = bucket_list_item.slice(0, -1);
				bucket_list_item = bucket_list_item.slice(1, bucket_list_item.length);
				const commaIdx = bucket_list_item.indexOf(',');
				const min = bucket_list_item.slice(0, commaIdx);
				const max = bucket_list_item.slice(commaIdx+1, bucket_list_item.length);
				bucket_list_item = "Min: " + min + "  /  Max: " + max;
			}
			console.log('bucket after', bucket_list_item);
			return(
				<div key={bucket.id}>
					<div style={{height: "25px", paddingLeft: "10px"}}>
						<span>{bucket_list_item}</span>{(props.deleteBucket) && <button style={{float: "right", height: "25px"}} onClick={props.deleteBucket.bind(null, bucket.id)}>x</button>}
					</div>
					<hr style={{margin: "0px", color: "red"}}/>
				</div>
			)
		})
	}

	return(
		<div>
			{listBuckets()}
		</div>
	)
}
