import { orm } from './models.babel.js';
import { combineReducers } from 'redux';

const initialState = orm.getEmptyState();

// function ormReducer(dbState, action) {
//     console.log('initial state', initialState)
//     console.log('orm reducers', orm)
//     console.log('dbstate', dbState)
//     const state = dbState || initialState
//     const session = orm.session(state)
//     console.log('session', session)

//     const { Survey } = session;
//     const { Node } = session;

//     console.log('survey>>>', Survey, 'node>>>>', Node)

//     switch (action.type) {
//         case 'ADD_SURVEY':
//             console.log('creating survey??', action.payload.survey)
//             // SURVEY.create(action.payload.survey);
//             // console.log('now we', session.state.Survey)
//             // break;

//             Survey.create(action.payload)
//             console.log('state', session.state)
//             break;
//         // case 'ADD_NODE_TO_SURVEY':
//         //     console.log('state', session.state)
//         //     console.log('adding node to survey??', action.payload.surveyId)
//         //     Survey.withId(action.payload.surveyId).nodes.add(action.payload.node)
//         //     break;
//     }
//     return session.state;
// }

// {
//   surveys: {
//     1: {
//       id: 1,
//       nodes: [10001]
//     }
//   },
//   nodes: {
//     10001: {
//       id: 10001
//     }
//   }
// }

function currentSurveyIdReducer(state = 0, action) {
    const { type, payload } = action;
    switch (type) {
    case 'UPDATE_CURRENT_SURVEY':
        return payload;
    default:
        return state;
    }
}


function survey(dbState, action) {
    console.log('being called survey')
    let newSurveyState;
    switch (action.type) {
        case 'UPDATE_SURVEY':
            console.log('ADD NODE FROM SURVEY')
            console.log(action.payload)

            let newNodeList = [];
            newNodeList.concat(state.nodes)
            newNodeList.push(action.payload.node)
            console.log(newNodeList)
            let newSurveyState = Object.assign({}, state.nodes, {id: action.payload.survey_id, nodes: newNodeList});
            console.log('newsurveystate', newSurveyState)
            // surveys(undefined, { type: 'UPDATE_SURVEY', payload: { survey: newSurveyState}})
            return newSurveyState;
        default:
            return state;
    }
}

function surveys(dbState, action) {
    console.log('being called surveys', action.type)
    let newSurvey;
    let newSurveys;
    let newSurveysState;
    let newState;
    switch (action.type) {
        // case 'ADD_SURVEY':
        //     console.log('add survey')
        //     newSurveys = {};
        //     newSurveys[action.payload.survey.id] = action.payload.survey;
        //     newSurveysState = Object.assign({}, state, newSurveys)
        //     console.log(newSurveysState)
        //     return newSurveysState;

        case 'UPDATE_SURVEYS':
            newState = Object.assign({}, state)
            newSurvey = state[action.payload.survey_id];
            console.log('update survey', newSurvey)
            let ok = Object.assign({}, newSurvey, action.payload.survey)

            newState[action.payload.survey_id] = ok;
            console.log(newState)
            newSurveysState = Object.assign({}, state, newState)
            console.log(newSurveysState)
            return newSurveysState;

        case 'DELETE_SURVEY': 
            newState = Object.assign({}, state)
            newState[action.payload.survey_id] = Object.assign({}, state[action.payload.survey_id])
            delete newState[action.payload.survey_id]
            return newState;

        case 'GET_SURVEY':
            return Object.assign({}, state[action.payload.id])
        default:
            return state;
    }
}

function nodes(dbState, action) {
    console.log('being called', state)
    let newNode;
    let newNodesState;
    switch (action.type) {
        case 'ADD_NODE':
            console.log('add node')
          
            newNode = {};
            newNode[action.payload.node.id] = action.payload.node;
            newNodesState = Object.assign({}, state, newNode)
            console.log(newNodesState)
            // survey(undefined, {type: 'ADD_NODE_TO_SURVEY', payload: action.payload})
            return newNodesState
        case 'UPDATE_NODE':
            console.log('update node from reducer');

            let nodeCopy = Object.assign({}, state[action.payload.id])

            if (action.payload.type=='sub_surveys') {
                nodeCopy.sub_surveys = action.payload.node;
            }

            if (action.payload.type=='node') {
                nodeCopy[action.payload.type] = action.payload[action.payload.type];
            }

            let newNode = {};
            newNode[action.payload.id] = nodeCopy;
            console.log('newnodede', newNode)
            newNodesState = Object.assign({}, state, newNode)
            console.log(newNodesState)
            return newNodesState

        case 'DELETE_NODE':
            console.log('action payload', action.payload.node_id)
            newNodesState = Object.assign({}, state)
            newNodesState[action.payload.node_id] = Object.assign({}, state[action.payload.node_id])
            delete newNodesState[action.payload.node_id]
            console.log('deleted node', newNodesState, action.payload.node_id)
            return newNodesState;
        case 'GET_NODE':
            return (Object.assign({}, state[action.payload.id]))
        default:
            return state;
    }
}

function surveyView(state = null, action) {
    switch (action.type) {
        case 'VIEW_SUBSURVEY':
            console.log('subsurvey showing, this.action.payload')
            if (action.payload.survey_id==1001 || !action.payload.survey_id) {
                console.log('null', action.payload.survey_id)
                return null;
            } else {
                console.log('not null')
                return Object.assign({}, {survey_id: action.payload.survey_id, nodeId: action.payload.nodeId, parent: action.payload.parent, bucket: action.payload.bucket})
            }
        default:
            return state;
    }
}


export default currentSurveyIdReducer;
