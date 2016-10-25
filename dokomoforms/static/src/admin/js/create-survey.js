var $ = require('jquery'),
    cookies = require('../../common/js/cookies');

console.log('hello from create-survey.js');

var modelSurvey = {
  title: {
    English: 'the test survey 4'
  },
  default_language: 'English',
  survey_type: 'public',
  metadata: {},
  nodes: [{
      node: {
        title: {English: 'test_question_1'},
        hint: {English: 'a hint'},
        type_constraint: 'integer',
        logic: {}
      }
    },
    {
      node: {
        title: {English: 'test_question_2'},
        hint: {English: 'a hint'},
        type_constraint: 'integer',
        logic: {}
      },
      sub_surveys: [
          {
            buckets: [
              {
                bucket_type: 'integer',
                bucket: '[1, 3]',
              }
            ],
            nodes: []
          }
      ]
    }
  ]
};

console.log(JSON.stringify(modelSurvey))

$('.btn').click(function() {
  console.log('this is working');
    $.ajax({
        type: "POST",
        url: "/api/v0/surveys",
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(modelSurvey),
        headers: {
          'X-XSRFToken': cookies.getCookie('_xsrf')
        },
        dataType: 'json',
        success: function(response) {
          console.log('success!!!');
        },
        error: function(response) {
          console.log(response.responseText);
        }
  });
});
