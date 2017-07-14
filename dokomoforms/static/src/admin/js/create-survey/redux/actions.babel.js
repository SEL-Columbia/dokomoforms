
export function denormalize() {
  console.log('denormalize action')
  return {
    type: "SUBMIT",
    payload: {survey: 1001}
  }
}

export function deleteAllBuckets(survey_id) {
  console.log('deleteBuckets')
  return {
    type: "DELETE_ALL_BUCKETS",
    payload: survey_id
  }
}

export function addNode(node) {
  console.log('you are adding a node!', node);
  return {
    type: "ADD_NODE",
    payload: node
  }
}

export function addQuestion(question) {
  console.log('you are adding a question', question);
  return {
    type: "ADD_QUESTION",
    payload: question
  }
}

export function addChoice(choice) {
  console.log('you are adding a choice', choice);
  return {
    type: "ADD_CHOICE",
    payload: choice
  }
}

export function updateNode(node) {
  console.log('you are updating a node', node.id);
  return {
    type: "UPDATE_NODE",
    payload: node
  }
}

export function updateChoice(choice) {
  console.log('you are updating a choice', choice);
  return {
    type: "UPDATE_CHOICE",
    payload: choice
  }
}

export function updateQuestion(question) {
  console.log('you are updating a question', question.id);
  return {
    type: "UPDATE_QUESTION",
    payload: question
  }
}

export function getNode(id) {
  return {
    type: "GET_NODE",
    payload: {id: id}
  }
}

export function addBucket(bucket) {
  console.log('add bucket being called', bucket)
  return {
    type: "ADD_BUCKET",
    payload: bucket
  }
}

export function addSurvey(sub_survey) {
  console.log('you are adding a survey!', sub_survey);
  return {
    type: "ADD_SURVEY",
    payload: sub_survey
  }
}

export function updateCurrentSurvey(surveyId) {
  console.log('you are updating the current survey!', surveyId);
  return {
    type: "UPDATE_CURRENT_SURVEY",
    payload: {surveyId: surveyId}
  }
}

export function getParentSurvey(surveyId) {
  console.log('you are updating the current survey!', surveyId);
  return {
    type: "UPDATE_CURRENT_SURVEY",
    payload: {surveyId: surveyId}
  }
}

export function getSurvey(id) {
  return {
    type: "GET_SURVEY",
    payload: {id: id}
  }
}

export function getBuckets(id) {
  return {
    type: "GET_BUCKETS",
    payload: {id: id}
  }
}

export function updateSurvey(survey) {
  console.log('you are updating survey', survey)
  return {
    type: "UPDATE_SURVEY",
    payload: survey
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
    payload: survey_id
  }
}

export function deleteChoice(choice_id) {
  console.log('you are removing', choice_id)
  return {
    type: "DELETE_CHOICE",
    payload: choice_id
  }
}

export function deleteNode(node_id) {
  console.log('you are removing', node_id)
  return {
    type: "DELETE_NODE",
    payload: node_id
  }
}

export function deleteBucket(bucket_id) {
  console.log('you are removing', bucket_id)
  return {
    type: "DELETE_BUCKET",
    payload: bucket_id
  }
}

export function addLogic(logic) {
  console.log('you are adding logic', logic)
  return {
    type: "ADD_LOGIC",
    payload: logic
  }
}

export function updateLogic(logic) {
  console.log('you are updating logic', logic)
  return {
    type: "UPDATE_LOGIC",
    payload: logic
  }
}

export function deleteLogic(logic_id) {
  console.log('you are deleting logic', logic_id)
  return {
    type: "DELETE_LOGIC",
    payload: logic_id
  }
}

