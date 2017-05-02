'use strict';

import { createSelector } from 'reselect';
import { createSelector as ormCreateSelector } from 'redux-orm';
import { orm } from './models.babel.js';


const ormSelector = state => state.orm;


// const denormalizeSelector = createSelector(
//     ormSelector,
//     state => state.submitted,
//     ormCreateSelector(orm, (session, submitted) => {
//         console.log('Running denormalized selector', submitted);
//         if (submitted) {
//             console.log('denormalizing')
//             return session.Survey.withId(1001).denormalize();
//         }
//         else return;
//     });
// );

const surveySelector = createSelector(
	ormSelector,
	state => state.currentSurveyId,
	ormCreateSelector(orm, (session, currentSurveyId) => {
    	console.log('Running survey selector', currentSurveyId);
    	
        const survey = session.Survey.withId(currentSurveyId);
        console.log('survey', survey)
        console.log('surveynodes', survey.nodes)
        console.log('surveybuckets', survey.buckets)

        let obj = survey.ref;

        console.log('obj')

        if (survey.buckets.toRefArray().length>0) {
            obj = Object.assign({}, obj, {
                buckets: survey.buckets.toRefArray()
            });
        };
        // let buckets = survey.buckets.toRefArray();
        // if (buckets.length) {
        //     the_survey = Object.assign({}, obj, {
        //         buckets: survey.buckets.toRefArray()
        //     })
        // }

        console.log('obj', obj)

		return Object.assign({}, obj, {
			nodes: survey.nodes.toRefArray()
		});
 	})
);


const parentSurveySelector = createSelector(
    ormSelector,
    state => state.currentSurveyId,
    ormCreateSelector(orm, (session, currentSurveyId) => {
        const parentNodeId = session.Survey.withId(currentSurveyId).node.id;
        console.log('parent selector', currentSurveyId, session.Node.withId(parentNodeId).survey.id);
        return session.Node.withId(parentNodeId).survey.id;
    })
);

const parentQuestionTitleSelector = createSelector(
    ormSelector,
    state => state.currentSurveyId,
    ormCreateSelector(orm, (session, currentSurveyId) => {
        const parentNodeId = session.Survey.withId(currentSurveyId).node.id;
        return session.Node.withId(parentNodeId).question.title;
    })
);

const pathSelector = createSelector(
    ormSelector,
    state => state.currentSurveyId,
    ormCreateSelector(orm, (session, currentSurveyId) => {

        let survey = session.Survey.withId(currentSurveyId);

        const path = [];

        while (survey) {
            if (!survey.node) break;
            
            const parentNode = survey.node;

            const title = parentNode.question.title;
            const buckets = parentNode.buckets || [];

            path.push({title: title, buckets: buckets})
            survey = parentNode.survey;
        }

        console.log('path', path);

        return path;

    })
);

const nodeSelector = createSelector(
    ormSelector,
    state => state.currentSurveyId,
    ormCreateSelector(orm, (session, currentSurveyId) => {
        console.log('Running node selector', currentSurveyId);
        // const nodes = session.Node.toModelArray().map(function(node){
        //     console.log('node', node.ref);
        //     console.log('model', node.model);
        //     if (node.model.sub_surveys) {
        //         console.log('yes')
        //         return Object.assign(node, {sub_surveys: node.sub_surveys.toRefArray()})
        //     }
        // });
        // const question = session.Node.withId(1).question;
        // console.log('question', question)
        const nodes = session.Survey.withId(currentSurveyId).nodes;
        console.log('nodes', nodes)
        // const nodes = session.Node.all();
        // let surveyNodes = nodes.filter(node => node.survey == currentSurveyId)
        // // surveyNodes = surveyNodes.toModelArray();
        // console.log('surveyNodes', surveyNodes)
        let surveyNodes = nodes.toModelArray().map(function(node){
            console.log('node', session.Question.withId(node.id))
            // const logic = node.logic ? node.logic.ref : {};
            const question = session.Question.withId(node.id).ref;
            console.log('question', question)
            let surveyNode = Object.assign({}, node.ref);

            if (node.sub_surveys.toRefArray().length>0) {
                surveyNode = Object.assign({}, surveyNode, {
                    sub_surveys: node.sub_surveys.toRefArray()
                });
            }
            // let surveys1 = session.Survey.all().toRefArray();
            // console.log(surveys1)
            // let subArray = session.Survey.all().filter(survey => survey.node == question.id)
            // subArray = subArray.toRefArray();
            // // console.log('arrayyyy', subArray)
            // if (subArray.length) return Object.assign({}, node, {sub_surveys: subArray})
            console.log(surveyNode)
            return surveyNode;
        });
        return surveyNodes;
    })
);


export { surveySelector,
        nodeSelector,
        parentSurveySelector,
        parentQuestionTitleSelector,
        pathSelector };

