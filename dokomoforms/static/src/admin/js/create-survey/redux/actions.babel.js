// export function addNode(node, survey_id) {
//   console.log('you are adding a node!', node.id, survey_id);
//   return {
//     type: "ADD_NODE_TO_SURVEY",
//     payload: {node: node, survey_id: survey_id}
//   }
// }

export function denormalize() {
  console.log('denormal action')
  return {
    type: "DENORMALIZE",
    payload: {survey: 1001}
  }
}
export function addNode(node, surveyId) {
  console.log('you are adding a node!');
  return {
    type: "ADD_NODE_TO_SURVEY",
    payload: {node: node, surveyId: surveyId}
  }
}

export function updateNode(id, node) {
  console.log('you are updating a node?!', id);
  return {
    type: "UPDATE_NODE",
    payload: {node_id: id, node: node}
  }
}

export function getNode(id) {
  return {
    type: "GET_NODE",
    payload: {id: id}
  }
}

export function addSurveyToNode(sub_survey, node_id) {
  console.log('you are adding a survey!');
  return {
    type: "ADD_SUBSURVEY_TO_NODE",
    payload: {sub_survey: sub_survey, node_id: node_id}
  }
}

// export function updateSurvey(survey) {
//   console.log('you are updating a survey!', id);
//   return {
//     type: "UPDATE_SURVEY",
//     payload: {survey: survey}
//   }
// }

export function getSurvey(id) {
  return {
    type: "GET_SURVEY",
    payload: {id: id}
  }
}

export function updateSurvey(survey_id, survey) {
  console.log('you are updating survey', survey, survey_id)
  return {
    type: "UPDATE_SURVEY",
    payload: {survey_id: survey_id, survey: survey}
  }
}

export function updateSurveyView(nodeId, survey_id, parent) {
  console.log('you are updating survey_view', nodeId, survey_id, parent)
  return {
    type: "VIEW_SUBSURVEY",
    payload: {nodeId: nodeId, survey_id: survey_id, parent: parent}
  }
}

export function deleteSurvey(survey_id) {
  console.log('you are removing', survey_id)
  return {
    type: "DELETE_SURVEY",
    payload: {survey_id: survey_id}
  }
}

export function deleteNode(node_id) {
  console.log('you are removing', node_id)
  return {
    type: "DELETE_NODE",
    payload: {node_id: node_id}
  }
}
// // // adding a new todo item

// // const ADD_TODO = 'ADD_TODO'

// // {
// // 	type: ADD_TODO,
// // 	text: 'Build my first Redux app'
// // }

// // {
// // 	type: TOGGLE_TODO,
// // 	index: UNIQUE INDEX of data being passed in
// // }

// // //changing the currently visisble todos
// // {
// // 	type: SET_VISIBILITY_FILTER,
// // 	filter: SHOW_COMPLETED
// // }

// // // action CREATORS return an action

// // function addTodo(text) {
// // 	return {
// // 		type: ADD_TODO,
// // 		text
// // 	}
// // }

// // // to initiate, pass the result to dispatch function

// // dispatch(addTodo(text))
// // dispatch(completeTodo(index))



// /*
//  * action types
//  */

// export const ADD_TODO = 'ADD_TODO'
// export const TOGGLE_TODO = 'TOGGLE_TODO'
// export const SET_VISIBILITY_FILTER = 'SET_VISIBILITY_FILTER'

// /*
//  * other constants
//  */


// /*
//  * action creators
//  */

// export function addNode(message) {
//   return {
//   	type: 'ADD_NODE',
//   	node: node
//   };
// }

// export function updateNode(index) {
//   return {
//   	type: 'TOGGLE_TODO',
//   	index: index
//   };
// }

