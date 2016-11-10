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

var test_survey = {
  title: {
    English: 'the test survey 341'
  },
  default_language: 'English',
  survey_type: 'public',
  metadata: {},
  nodes: [{
      node: {
        title: {English: 'What is your age?'},
        hint: {English: 'a hint'},
        type_constraint: 'integer',
        logic: {}
      }
    },
    {
      node: {
        title: {English: 'Do you smoke currently or have you ever smoked?'},
        hint: {English: 'a hint'},
        type_constraint: 'multiple_choice',
        choices: [
            {
                choice_text: {
                    English: 'yes, I currently smoke'
                }
            },
            {
                choice_text: {
                    English: 'I do not currently smoke, but I have in the past.'
                }
            },
            {
                choice_text: {
                    English: 'no, I have never smoked'
                }
            }
        ]
      },
      sub_surveys: [
            {
                buckets: [
                    {
                        bucket_type: 'multiple_choice',
                        bucket: {
                            'choice_number': 0
                        }
                    },
                    {
                        bucket_type: 'multiple_choice',
                        bucket: {
                            'choice_number': 1
                        }
                    }
                ],
                nodes: [
                    {
                        node: {
                            title: {English: 'When did you start?'},
                            type_constraint: 'date'
                        }
                    }
                ]
            },
            {
               buckets: [
                    {
                        bucket_type: 'multiple_choice',
                        bucket: {
                            'choice_number': 1
                        }
                    }
                ],
                nodes: [
                    {
                        node: {
                            title: {English: 'When did you quit?'},
                            type_constraint: 'date'
                        }
                    }
                ] 
            }
        ]
    },
    {
        node: {
            title: {English: 'Do you drink?'},
            type_constraint: 'multiple_choice',
            choices: [
                {
                    choice_text: {
                        English: 'yes'
                    }
                },
                {
                    choice_text: {
                        English: 'no'
                    }
                }
            ]
        }
    }]
}

console.log(JSON.stringify(modelSurvey))

$('#AJAXBTN').click(function() {
  console.log('this is working');
    $.ajax({
        type: "POST",
        url: "/api/v0/surveys",
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(test_survey),
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
