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
	state => state.currentSurveyId,
	ormCreateSelector(orm, (session, currentSurveyId) => {
    	console.log('Running survey selector', currentSurveyId);
    	const survey = session.Survey.withId(currentSurveyId)
        const obj = survey.ref;

        const testnodes = survey.nodes.toRefArray();
        console.log('obj', obj)
        console.log('nodes', testnodes)
		return Object.assign({}, obj, {
			nodes: survey.nodes.toRefArray()
		})
 	})
);

const nodesSelector = createSelector(
    ormSelector,
    state => state.orm,
    ormCreateSelector(orm, (session, orm) => {
        console.log('Running node selector', session);
        return session.Node.all().toRefArray().map(node => {
            
            const obj = node.ref;

            console.log('without', node.sub_surveys)
            console.log('with', node.sub_surveys.toRefArray())

            return Object.assign({}, obj, {
                sub_surveys: node.sub_surveys.toRefArray()
            })
        })
    })
);

const nodeSelector = createSelector(
    ormSelector,
    state => state.currentSurveyId,
    ormCreateSelector(orm, (session, currentSurveyId) => {
        console.log('Running node selector>>>>', currentSurveyId);
        return session.Node.filter({survey: currentSurveyId}).toModelArray().map(node => {
            const obj = node.ref;
            console.log(obj);
            return Object.assign({}, obj, {
                sub_surveys: node.sub_surveys.toRefArray()
            })
        })
    })
);



export {surveySelector, nodeSelector};