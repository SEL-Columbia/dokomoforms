import { ORM, oneToOne, fk, many, attr, Model } from 'redux-orm';


class CRUDModel extends Model {
    static reducer(action, ConcreteModel, session) {
        console.log('getting called', ConcreteModel.modelName)
        let modelName = ConcreteModel.modelName.toUpperCase();
        console.log(modelName)
        // modelName = modelName == 'QUESTION' ? 'NODE' : modelName;
        switch (action.type) {
            case 'ADD_' + modelName:
                ConcreteModel.create(action.payload);
                break;
            case 'UPDATE_' + modelName:
                ConcreteModel.withId(action.payload.id).update(action.payload);
                break;
            case 'DELETE_' + modelName:
                console.log('remove', action.payload, ConcreteModel)
                ConcreteModel.withId(action.payload).delete();
                break;
        }
        return undefined;
    }
}


class Question extends CRUDModel {
    denormalize() {
        let data;
        const logic = session.Question.withId(id).logic;
        if (logic) data = Object.assign({logic: logic.ref})
        data = Object.assign({}, this.ref)
        delete data.id;
        delete data.node;
        return data;
    }
}

Question.fields = {
    id: attr(),
    node: oneToOne('Node', 'question')
};

Question.modelName = 'Question';


class Node extends CRUDModel {
    denormalize() {
        console.log('this', this)
        const sub_surveys = this.sub_surveys.toModelArray().map(sub_survey => sub_survey.denormalize())
        const question = this.question.modelClass.withId(this.id).denormalize();
        console.log('the question', question)
        let data = Object.assign({}, this.ref, {node: question})
        if (sub_surveys.length) data = Object.assign(data, {sub_surveys: sub_surveys})
        delete data.id
        delete data.survey
        delete data.question
        return data;
    }
	// static reducer(action, Node, session) {
	// 	const { payload, type } = action;
	// 	switch (type) {
	// 		case "ADD_NODE_TO_SURVEY":
	// 			console.log('state', session.state)
 //            	console.log('adding node to survey', payload.node)
 //            	let thenode = Node.create(payload.node).initiate()
 //            	console.log('new state', thenode)
 //            	break;
 //            case "UPDATE_NODE":
 //                console.log('updating node');
 //            	Node.withId(payload.id).update(payload);
 //            	break;
 //            // case "ADD_SUBSURVEY_TO_NODE":
 //            //     console.log('survey to node model reducer')
 //            //     Node.withId(payload.nodeId.sub_surveys.add(payload.sub_survey);
 //            //     break;
 //           	case "DELETE_NODE":
 //           		console.log('deleting node from models', payload.node_id)
 //           		Node.withId(payload.node_id).delete();
 //        		break;
 //        }
 //        return undefined;
	// }

}

Node.modelName = 'Node';

// Declare your related fields.
Node.fields = {
    id: attr(),
    survey: fk('Survey', 'nodes')
};

class Survey extends CRUDModel {
    denormalize(){
        console.log('this', this.nodes)
        const nodes = this.nodes.toModelArray().map(node => node.denormalize());
        const buckets = this.buckets.toModelArray().map(bucket => bucket.denormalize());
        let data = Object.assign({}, this.ref, {nodes: nodes})
        if (buckets.length) data = Object.assign(data, {buckets: buckets})
        delete data.id;
        delete data.node;
        return data;
    }





    // denormalize(survey){
    //     console.log('denormal')
    //     console.log('denormal', survey)

    //     const denormalizedSurvey = Survey.withId(survey).ref

    //     const denormalizedBuckets = [];

    //     if (Survey.withId(survey).buckets) {
    //         Survey.withId(survey).buckets.toRefArray().map(bucket => {
    //             const obj = bucket;
    //             console.log('bucket', obj)
    //             denormalizedBuckets.push(obj.bucket);
    //         })
    //     }

    //     const denormalizedNodes = Survey.withId(survey).nodes.toModelArray().map(node => {

    //         const obj = node.ref;

    //         console.log('node', node)
    //         console.log('obj', obj)


    //         const sub_surveys = node.sub_surveys.toModelArray().map(sub_survey => {
    //                 return sub_survey.ref
    //         })

    //         console.log('subsurveys', sub_surveys)

    //         const denormalized = [];

    //         if (sub_surveys.length > 0) {
    //                 node.sub_surveys.toRefArray().map(function(sub_survey) {
    //                     console.log('pre test', sub_survey)
    //                     let test = denormalize(sub_survey.id)
    //                     console.log('test', test)
    //                     denormalized.push(test)
    //             })
    //         }

    //         // node.sub_surveys.toModelArray().map(sub_survey => {
    //         //     // const obj = survey.ref;
    //         //     console.log('just called')
    //         //     console.log('mapping subs', sub_survey)
    //         //     // denormalize('obj', sub_survey.ref.id)
    //         // })

    //         const newNode = Object.assign({}, obj, {
    //             sub_surveys: denormalized
    //         })

    //         delete newNode.id
    //         delete newNode.survey

    //         if (newNode.node.choices) {
    //             let choices_list = [];
    //             choices_list = newNode.node.choices.map(function(choice){
    //                 delete choice.id;
    //                 return {choice_text: choice};
    //             })
    //             newNode.node.choices = choices_list;
    //         }

    //         if (!newNode.sub_surveys.length) {
    //             delete newNode.sub_surveys
    //         }
    //         console.log('newww node', newNode)
    //         return newNode;
    //     })

    //     console.log('denormalized survey', denormalizedSurvey)
    //     console.log('denormalized nodes', denormalizedNodes)

    //     let newSurvey = Object.assign({}, denormalizedSurvey, {
    //         nodes: denormalizedNodes})

    //     console.log('near end', denormalizedBuckets)
    //     if (denormalizedBuckets && denormalizedBuckets.length) {
    //         newSurvey = Object.assign({}, newSurvey, {
    //             buckets: denormalizedBuckets
    //         });
    //     }

    //     delete newSurvey.id
    //     delete newSurvey.node
    //     delete newSurvey.list

    //     console.log("!!", newSurvey)
    //     return newSurvey;
    //     // Survey.withId(1001).update({denormalized: newSurvey});
    // }
};

Survey.modelName = 'Survey';

// Declare your related fields.
Survey.fields = {
    id: attr(),
    default_language: attr(),
    node: fk('Node', 'sub_surveys')
};


class Bucket extends CRUDModel {
    denormalize() {
        const data = Object.assign({}, this.ref)
        delete data.id;
        delete data.survey;
        return data;
    }
};

Bucket.modelName = 'Bucket';

// Declare your related fields.
Bucket.fields = {
    id: attr(), // non-relational field for any value; optional but highly recommended
    bucket_type: attr(),
    bucket: attr(),
    survey: fk('Survey', 'buckets')
};


class Logic extends CRUDModel {};

    Logic.modelName = 'Logic';

    // Declare your related fields.
    Logic.fields = {
        id: attr(), // non-relational field for any value; optional but highly recommended
        question: oneToOne('Question', 'logic')
};


const orm = new ORM();
orm.register(Survey, Node, Bucket, Question, Logic);

console.log('new orm', orm)

export {Survey, Bucket, Question, Logic, orm}
