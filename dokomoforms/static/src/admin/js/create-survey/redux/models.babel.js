import { ORM, fk, many, attr, Model } from 'redux-orm';

console.log('orm', ORM)

class Node extends Model {
	static reducer(action, Node, session) {
		const { payload, type } = action;
		switch (type) {
			case "ADD_NODE_TO_SURVEY":
				console.log('state', session.state)
            	console.log('adding node to survey??', payload.node)
            	Node.create(payload.node)
            	console.log('new state????', session.state)
            	break;
            case "UPDATE_NODE":
            	Node.withId(payload.node_id).update({node: payload.node});
            	break;
            case "ADD_SUBSURVEY_TO_NODE":
            	console.log('node model', payload.node_id, payload.sub_survey)
            	Node.withId(payload.node_id).sub_surveys.add(payload.sub_survey.id);
            	break;
           	case "DELETE_NODE":
           		console.log('deleting node from models', payload.node_id)
           		Node.withId(payload.node_id).delete();
        		break;
        }
        return undefined;
	}
};

Node.modelName = 'Node';

// Declare your related fields.
Node.fields = {
    id: attr(), // non-relational field for any value; optional but highly recommended
    node: attr(),
    sub_surveys: many('Survey', 'node_model')
};

class Survey extends Model {
	static reducer(action, Survey, session) {
		const { payload, type } = action;
		switch (type) {
			case "ADD_SUBSURVEY_TO_NODE":
                console.log('survey to node model reducer')
            	Survey.create(payload.sub_survey);
            	break;
			case "ADD_NODE_TO_SURVEY":
				console.log('state', session.state)
            	console.log('adding node to survey??', payload.surveyId, payload.node)
            	Survey.withId(payload.surveyId).nodes.add(payload.node.id)
            	console.log('new state????', session.state)
            	break;
            case "UPDATE_SURVEY":
            	console.log('update survey', payload)
            	Survey.withId(payload.survey_id).update(payload.survey)
            	console.log('after state', session.state)
            	break;
            case "DELETE_SURVEY":
            	Survey.withId(payload.survey_id).delete();
            	break;
            case "DENORMALIZE":
            console.log('from model');
                // const survey1 = Survey.withId(payload.survey)
                let counter = 0;
                function denormalize(survey){
                    console.log('sur', survey)
                    counter++;
                    if (counter > 4) {
                        return;
                    }

                    const denormalizedSurvey = Survey.withId(survey).ref

                    const denormalizedNodes = Survey.withId(survey).nodes.toModelArray().map(node => {
            
                        const obj = node.ref;

                        console.log('node', node)
                        console.log('obj', obj)


                        const sub_surveys = node.sub_surveys.toModelArray().map(sub_survey => {
                                return sub_survey.ref
                        })

                        console.log('subsurveys', sub_surveys)

                        const denormalized = [];

                        if (sub_surveys.length) {
                                node.sub_surveys.toModelArray().map(function(sub_survey) {
                                    let test = denormalize(sub_survey.ref.id)
                                    console.log('test', test)
                                    denormalized.push(test)
                            })
                        }

                        // node.sub_surveys.toModelArray().map(sub_survey => {
                        //     // const obj = survey.ref;
                        //     console.log('just called')
                        //     console.log('mapping subs', sub_survey)
                        //     // denormalize('obj', sub_survey.ref.id)
                        // })

                        const newNode = Object.assign({}, obj, {
                            sub_surveys: denormalized
                        })

                        if (!sub_surveys.length) {
                            delete newNode.sub_surveys
                        }
                        console.log('newww node', newNode)
                        return newNode;
                    })

                    console.log('denormalized survey', denormalizedSurvey)
                    console.log('denormalized nodes', denormalizedNodes)

                    const newSurvey = Object.assign({}, denormalizedSurvey, {
                        nodes: denormalizedNodes})

                    console.log("!!", newSurvey)
                    return newSurvey;
            }
            denormalize(payload.survey)
	   }
    return undefined;
    }
};

Survey.modelName = 'Survey';

// Declare your related fields.
Survey.fields = {
    id: attr(),
    title: attr(),
    default_language: attr(),
    nodes: many('Node', 'survey_model')
};


const orm = new ORM();
orm.register(Survey, Node);

console.log('new orm', orm)

export {Node, Survey, orm}