import { ORM, oneToOne, fk, many, attr, Model } from 'redux-orm';


class CRUDModel extends Model {
    static reducer(action, ConcreteModel, session) {
        console.log('getting called crudmodel', ConcreteModel.modelName)
        let modelName = ConcreteModel.modelName.toUpperCase();
        console.log(modelName);
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
            case 'SUBMIT':
                if (modelName!=='SURVEY') break;
                ConcreteModel.withId(1001).denormalize();
        }
        return undefined;
    }
}


class Question extends CRUDModel {
    denormalize() {
        console.log('question denormalize', this.ref)
        let data = Object.assign({}, this.ref)
        if (this.logic) {
            console.log('denormalize logic', this.logic.ref)
            const logic = this.logic.denormalize();
            data = Object.assign(data, {logic: logic})
        }
        if (this.multiple_choices) {
            let choices = this.multiple_choices.toRefArray().map(function(choice){
                console.log('mapping through choices', choice)
                return Object.assign({}, {choice_text: choice.choice_text});
            });
            if (choices.length) data = Object.assign(data, {choices: choices})
        }
        console.log('question data', data)
        delete data.id;
        delete data.node;
        return data;
    }
}

Question.fields = {
    id: attr(),
    node: oneToOne('Node'),
    allow_multiple: attr(),
    type_constraint: attr()
};

Question.modelName = 'Question';


class Node extends CRUDModel {
    denormalize() {
        console.log('this', this.ref)
        const sub_surveys = this.sub_surveys.toModelArray().map(sub_survey => sub_survey.denormalize())
        console.log('this id', this.ref.id)
        const question = this.question.denormalize();
        // console.log('the question', question)
        // const questionNode = Object.assign({}, question)
        let data = Object.assign({}, this.ref, {node: question})
        if (sub_surveys.length) data = Object.assign(data, {sub_surveys: sub_surveys})
        console.log('data before deletion', data)
        delete data.id
        delete data.survey
        // delete data.question
        console.log('data after deletion', data)
        return data;
    }
}

Node.modelName = 'Node';

Node.fields = {
    id: attr(),
    survey: fk('Survey', 'nodes')
};


class Survey extends CRUDModel {
    denormalize(){
        console.log('this survey', this.ref)
        console.log('nodes', this.nodes.toRefArray())
        const nodes = this.nodes.toModelArray().map(node => node.denormalize());
        const buckets = this.buckets.toModelArray().map(bucket => bucket.denormalize());
        let data = Object.assign({}, this.ref, {nodes: nodes})
        if (buckets.length) data = Object.assign(data, {buckets: buckets})
        console.log('this data', this.ref.id, data)
        delete data.id;
        delete data.node;
        return data;
    }
};

Survey.modelName = 'Survey';

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

Bucket.fields = {
    id: attr(), // non-relational field for any value; optional but highly recommended
    bucket_type: attr(),
    bucket: attr(),
    survey: fk('Survey', 'buckets')
};


class Logic extends CRUDModel {
    denormalize() {
        const data = Object.assign({}, this.ref)
        delete data.id
        delete data.question
        return data
    }
};

Logic.modelName = 'Logic';

Logic.fields = {
    id: attr(),
    question: oneToOne('Question')
};


class Choice extends CRUDModel {};

Choice.modelName = 'Choice';

Choice.fields = {
    id: attr(),
    question: fk('Question', 'multiple_choices')
}


const orm = new ORM();
orm.register(Survey, Node, Question, Bucket, Logic, Choice);

console.log('new orm', orm)

export {Survey, Node, Question, Bucket, Logic, Choice, orm}
