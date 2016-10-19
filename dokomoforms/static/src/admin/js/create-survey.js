var $ = require('jquery'),
    cookies = require('../../common/js/cookies');


var newSurvey = {
  title: {
    English: 'the test survey 2'
  },
  default_language: 'English',
  survey_type: 'public',
  metadata: {},
  nodes: [{
    node: {
      title: {English: 'test_question'},
      hint: {English: 'a hint'},
      type_constraint: 'text',
      logic: {}
    },
    node: {
      title: {English: 'test_question2'},
      hint: {English: 'a hint'},
      type_constraint: 'text',
      logic: {}
    }
  }]
};

console.log(JSON.stringify(newSurvey))

$('.btn').click(function() {
  console.log('this is  working');
    $.ajax({
    type: "POST",
    url: "/api/v0/surveys",
    contentType: 'application/json',
    processData: false,
    data: JSON.stringify(newSurvey),
    headers: {
      'X-XSRFToken': cookies.getCookie('_xsrf')
    },
    dataType: 'json',
    success: function(response) {
      console.log('success!!!');
    },
    error: function(response) {
      console.log(response);
    }
  });

});
