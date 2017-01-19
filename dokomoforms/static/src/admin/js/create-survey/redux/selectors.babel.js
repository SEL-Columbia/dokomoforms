import { createSelector } from 'reselect';
import { createSelector as ormCreateSelector } from 'redux-orm';

import { orm } from './models.babel.js';


// import { ORM, createReducer, createSelector } from 'redux-orm';

// import { Survey, Node, orm } from './models.babel.js';

// console.log('redux', reduxReducer)
// const surveySelector = createSelector(orm, state => state.orm, session => {
//     console.log('session from select', session)
// });

// const surveySelector = createSelector(orm, state => state.orm, session => {
// 	console.log('select', session)
// 	const here = session.Survey.all().toRefArray();
// 	console.log('here', here)
// });


const ormSelector = state => state.orm;


const surveySelector = createSelector(
	ormSelector,
	state => state.orm,
	ormCreateSelector(orm, (session, orm) => {
    	console.log('Running user selector', session);
    	return session.Survey.all().toModelArray().map(survey => {
    		
    		const obj = survey.ref;

    		console.log('without', survey.nodes)
    		console.log('with', survey.nodes.toRefArray())

    		return Object.assign({}, obj, {
    			nodes: survey.nodes.toRefArray()
    		})

    	})
 	})
);





export default surveySelector;