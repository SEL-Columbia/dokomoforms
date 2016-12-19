import utils from './../utils.js';
import MultipleChoice from './MultipleChoice.babel.js';
import { Title, FacilityLogic, MinMaxLogic } from './Logic.babel.js';

class SubSurveyList extends React.Component {

	constructor(props) {
        super(props);

        this.addBucket = this.addBucket.bind(this);
        this.goToSubSurvey = this.goToSubSurvey.bind(this)

        this.state = {
        	buckets: [],
        	nodes: ['I am subsurvey node']
        }
    }

    addBucket(event) {
    	let copy = [];
    	copy = copy.concat(this.state.buckets)
    	copy.push(event.target.value)
    	this.setState({buckets: copy}, function(){
    		console.log('added bucket', this.state.buckets)
    	})
    }

    goToSubSurvey() {
    	console.log('props', this.props)
    	console.log('goto subsurvey', this.state.buckets[0], this.props.id)
    	this.props.goToSubSurvey(this.state.buckets[0], this.props.id)
    }

	render(){
		console.log('from subsurvey', this.props)
		return(
			<div>
			SubSurvey List
				<div>
					<div>
						Bucket: <input onBlur={this.addBucket}></input>
					</div>
					<div>
						<button onClick={this.goToSubSurvey}>SubSurvey</button>
					</div>
				</div>
				<button>add subsurvey</button>
			</div>
		)
	}
}

export default SubSurveyList