// var $ = require('jquery'),
//     cookies = require('../../common/js/cookies');

// console.log('hello from create-survey.js');

// var modelSurvey = {
//   title: {
//     English: 'languages survey'
//   },
//   default_language: 'English',
//   survey_type: 'public',
//   metadata: {},
//   languages: ['English', 'German', 'French']
//   nodes: [{
//       node: {
//         title: {English: 'test_question_1',
//                 German: 'test_question_1_g'},
//                 French: 'test_question_1_f'}
//         hint: {English: 'a hint'},
//         type_constraint: 'integer',
//         logic: {}
//       }
//     },
//     {
//       node: {
//         title: {English: 'test_question_2'},
//         hint: {English: 'a hint'},
//         type_constraint: 'integer',
//         logic: {}
//       }
//     }
//   ]
// };

// var test_survey = {
//   title: {
//     English: 'repeatable test'
//   },
//   default_language: 'English',
//   survey_type: 'public',
//   metadata: {},
//   nodes: [{
//       node: {
//         title: {English: 'What is your age?'},
//         hint: {English: 'a hint'},
//         type_constraint: 'integer',
//         logic: {}
//       }
//     },
//     {
//       node: {
//         title: {English: 'Do you smoke currently or have you ever smoked?'},
//         hint: {English: 'a hint'},
//         type_constraint: 'multiple_choice',
//         choices: [
//             {
//                 choice_text: {
//                     English: 'yes, I currently smoke'
//                 }
//             },
//             {
//                 choice_text: {
//                     English: 'I do not currently smoke, but I have in the past.'
//                 }
//             },
//             {
//                 choice_text: {
//                     English: 'no, I have never smoked'
//                 }
//             }
//         ]
//       },
//       sub_surveys: [
//             {
//                 buckets: [
//                     {
//                         bucket_type: 'multiple_choice',
//                         bucket: {
//                             'choice_number': 0
//                         }
//                     },
//                     {
//                         bucket_type: 'multiple_choice',
//                         bucket: {
//                             'choice_number': 1
//                         }
//                     }
//                 ],
//                 nodes: [
//                     {
//                         node: {
//                             title: {English: 'When did you start?'},
//                             type_constraint: 'date'
//                         }
//                     }
//                 ]
//             },
//             {
//                buckets: [
//                     {
//                         bucket_type: 'multiple_choice',
//                         bucket: {
//                             'choice_number': 1
//                         }
//                     }
//                 ],
//                 nodes: [
//                     {
//                         node: {
//                             title: {English: 'When did you quit?'},
//                             type_constraint: 'date'
//                         }
//                     }
//                 ] 
//             }
//         ]
//     },
//     {
//         node: {
//             title: {English: 'Do you drink?'},
//             type_constraint: 'multiple_choice',
//             choices: [
//                 {
//                     choice_text: {
//                         English: 'yes'
//                     }
//                 },
//                 {
//                     choice_text: {
//                         English: 'no'
//                     }
//                 }
//             ]
//         }
//     }]
// }

// console.log(JSON.stringify(modelSurvey))

// $('#AJAXBTN').click(function() {
//   console.log('this is working');
//     $.ajax({
//         type: "POST",
//         url: "/api/v0/surveys",
//         contentType: 'application/json',
//         processData: false,
//         data: JSON.stringify(test_survey),
//         headers: {
//           'X-XSRFToken': cookies.getCookie('_xsrf')
//         },
//         dataType: 'json',
//         success: function(response) {
//           console.log('success!!!');
//         },
//         error: function(response) {
//           console.log(response.responseText);
//         }

//       //   sub_surveys: [
//       //     {
//       //       buckets: [
//       //         {
//       //           bucket_type: 'integer',
//       //           bucket: '[1, 3]',
//       //         }
//       //       ],
//       //       nodes: []
//       //     }
//       // ]
//   });
// });


// Object {submitter_name: "test_user",
// 	 	submitter_email: "test_creator@fixtures.com",
// 		survey_id: "9d4c9f3d-ec45-444b-b202-7c3c83c527a0",
// 		answers: Array[4],
		

// {submitter_name : "test_user",
// submitter_email : "test_creator@fixtures.com",
// survey_id: "9d4c9f3d-ec45-444b-b202-7c3c83c527a0",
// answers:[{
// 	response:{
// 		response:3,
// 		response_type: "answer",
// 		type_constraint: "integer",
// 		survey_node_id: "0bbbfc90-c032-448e-9409-e8319d0ec1be"
// 	},
// 	response:{
// 		response: "one",
// 		response_type: "answer",
// 		type_constraint: "text",
// 		survey_node_id: "f60a7e5f-76fa-4daf-8327-f21872940ccc"
// 	}
// 		\"response\":{\"response\":\"one\",\"response_type\":\"answer\"},\"type_constraint\":\"text\"},{\"survey_node_id\":\"0bbbfc90-c032-448e-9409-e8319d0ec1be\",\"response\":{\"response\":\"two\",\"response_type\":\"answer\"},\"type_constraint\":\"text\"},{\"survey_node_id\":\"0bbbfc90-c032-448e-9409-e8319d0ec1be\",\"response\":{\"response\":\"three\",\"response_type\":\"answer\"},\"type_constraint\":\"text\"}],\"start_time\":\"2017-01-23T19:28:01.650Z\",\"save_time\":\"2017-01-23T19:28:15.804Z\",\"submission_time\":\"\"}"
// 	}




// {"submitter_name":"test_user",
// "submitter_email":"test_creator@fixtures.com",
// "survey_id":"9d4c9f3d-ec45-444b-b202-7c3c83c527a0",
// "answers":[
// 	{"survey_node_id":"f60a7e5f-76fa-4daf-8327-f21872940ccc",
// 	"response":{"response":3,
// 		"response_type":"answer"},
// 	"type_constraint":"integer"},
// 	{"survey_node_id":"0bbbfc90-c032-448e-9409-e8319d0ec1be",
// 	"response":{"response":"one",
// 		"response_type":"answer"},
// 	"type_constraint":"text"},
// 	{"survey_node_id":"0bbbfc90-c032-448e-9409-e8319d0ec1be",
// 	"response":{"response":"two",
// 		"response_type":"answer"},
// 	"type_constraint":"text"},
// 	{"survey_node_id":"0bbbfc90-c032-448e-9409-e8319d0ec1be",
// 	"response":{"response":"three",
// 		"response_type":"answer"},
// 		"type_constraint":"text"}
// 	],
// 	"start_time":"2017-01-23T19:28:01.650Z",
// 	"save_time":"2017-01-23T19:28:15.804Z",
// 	"submission_time":""
// }


// {"submitter_name":"test_user",
// "submitter_email":"test_creator@fixtures.com",
// "survey_id":"9d4c9f3d-ec45-444b-b202-7c3c83c527a0",
// "answers":[
// 	{"survey_node_id":"58d932ab-2889-4568-a160-5e8183069e26",
// 	"response":{"response":1,"response_type":"answer"},
// 	"type_constraint":"integer"}
// 	,
// 	{"survey_node_id":"51950273-8d5f-4d65-871d-6c8773116278",
// 	"response":{"response":"uno","response_type":"answer"},
// 	"type_constraint":"text"}],
// "start_time":"2017-01-23T20:16:43.566Z",
// "save_time":"2017-01-23T20:16:51.397Z",
// "submission_time":""}



// var oisu = {
//   title: {
//     English: 'int bucket test'
//   },
//   default_language: 'English',
//   survey_type: 'public',
//   nodes: [
//     {
//       node: {
//         title: {English: 'the bucket is [5)'},
//         hint: {English: 'a hint'},
//         type_constraint: 'integer',
//       },
//       sub_surveys: [
//             {
//                 buckets: [
//                     {
//                         bucket_type: 'integer',
//                         bucket: '[5)'
//                     }
//                 ],
//                 nodes: [
//                     {
//                         node: {
//                             title: {English: 'you picked over five - give integer answer'},
//                             type_constraint: 'integer'
//                         }
//                     }
//                 ]
//             },
//       ]
//     }]
// }


