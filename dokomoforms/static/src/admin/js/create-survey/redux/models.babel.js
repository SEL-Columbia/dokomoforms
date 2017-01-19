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
        }
        return undefined;
	}
};

Node.modelName = 'Node';

// Declare your related fields.
Node.fields = {
    id: attr(), // non-relational field for any value; optional but highly recommended
    node: attr()
};

class Survey extends Model {
	static reducer(action, Survey, session) {
		const { payload, type } = action;
		switch (type) {
			case "ADD_NODE_TO_SURVEY":
				console.log('state', session.state)
            	console.log('adding node to survey??', payload.surveyId, payload.node)
            	Survey.withId(payload.surveyId).nodes.add(payload.node.id)
            	console.log('new state????', session.state)
            	break;
        }
        return undefined;
	}
};

Survey.modelName = 'Survey';

// Declare your related fields.
Survey.fields = {
    id: attr(),
    default_language: attr(),
    nodes: many('Node')
};


const orm = new ORM();
orm.register(Survey, Node);

console.log('new orm', orm)

export {Node, Survey, orm}