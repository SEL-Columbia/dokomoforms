import { createSelector } from 'reselect';
import { createSelector as ormCreateSelector } from 'redux-orm';
import { orm } from './models.babel.js';


const ormSelector = state => state.orm;


const denormalizeSelector = createSelector(
    ormSelector,
    state => state.currentSurveyId,
    ormCreateSelector(orm, (session, currentSurveyId) => {
        console.log('Running survey selector', currentSurveyId);
        const survey = session.Survey.withId(1001);
        const denormalized = survey.denormalize();
        return denormalized;
    })
);


const surveySelector = createSelector(
	ormSelector,
	state => state.currentSurveyId,
	ormCreateSelector(orm, (session, currentSurveyId) => {
    	console.log('Running survey selector', currentSurveyId);
    	const survey = session.Survey.withId(currentSurveyId);
        const obj = survey.ref;

        console.log('survey', survey)
        console.log('surveynodes', survey.nodes)

        let buckets = [];
        let the_survey = {};
        if (survey.buckets) buckets = survey.buckets.toRefArray();
        if (buckets.length) {
            the_survey = Object.assign({}, obj, {
                buckets: survey.buckets.toRefArray()
            })
        }

        console.log('obj', obj)
        console.log('nodes', nodes)
		the_survey = Object.assign({}, the_survey, obj, {
			nodes: survey.nodes.toRefArray()
		})

        return the_survey;
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
        const nodes = session.Node.all();
        let surveyNodes = nodes.filter(node => node.survey == currentSurveyId)
        surveyNodes = surveyNodes.toModelArray();
        console.log('surveyNodes', surveyNodes)
        surveyNodes = surveyNodes.map(function(node){
            console.log('ndee', session.Question.withId(node.id))
            // const logic = node.logic ? node.logic.ref : {};
            const question = session.Question.withId(node.id).ref;
            node = Object.assign({}, node.ref, {question: question});
            let subArray = session.Survey.filter(survey => survey.node == node.id)
            subArray = subArray.toRefArray();
            console.log('arrayyyy', subArray)
            if (subArray.length) return Object.assign({}, node, {sub_surveys: subArray})
            console.log(node)
            return node;
        })
        console.log(surveyNodes);
        return surveyNodes;
        // console.log(survey_nodes);

        // let surveynodes1 = {};
        // const surveynodes = survey_nodes.toModelArray().map(function(node){
        //     console.log(node.sub_surveys)
        //     if (node.sub_surveys) surveynodes1[node.id] = node.sub_surveys;
        // })
        // console.log(surveynodes1);
        // return session.Node.all().toRefArray().filter(node => node.survey == currentSurveyId).map(node => {
        //     const obj = Object.assign({}, node);
        //     console.log('obj', obj)
        //     const subs = node.sub_surveys.toRefArray();
        //     if (subs.length) obj.sub_surveys = subs;

        //     return obj
        // })
        // const obj = survey.ref;

        // const testnodes = survey.nodes.toRefArray();
        // console.log('obj', obj)
        // console.log('nodes', testnodes)

        // return Object.assign({}, obj, {
        //     nodes: survey.nodes.toRefArray()
        // })


        // // let nodes = session.Node.all().filter(node => node.survey == currentSurveyId)
        // nodes.toModelArray().map(function(node){
        //     if (node.sub_surveys) {
        //         console.log('not ref', sub)
        //         return Object.assign(node, node.sub_surveys.toRefArray());
        //     }
        //     return node.ref;
        // })
        // let subObj = {};
        // if (subsurveys) {
        //     subObj = {sub_surveys: subsurveys}
        // }
        // return nodes.toRefArray();
    })
);



export {surveySelector, nodeSelector, parentSurveySelector, denormalizeSelector};


