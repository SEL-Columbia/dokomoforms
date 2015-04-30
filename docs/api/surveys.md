## Dokomo REST API

# Surveys

1. [List Surveys](#list-surveys)
2. [Get a Single Survey](#single-survey)
3. [Create a New Survey](#create-survey)
4. [Update an Existing Survey](#update-survey)
5. [Delete a Survey](#delete-survey)
6. [Submit to a Survey](#survey-submit)
7. [List Submissions to a Survey](#survey-submissions)
8. [Get Stats for a Single Survey](#survey-stats)
9. [Get Submission Activity for All Surveys](#all-surveys-activity)
10. [Get Submission Activity for a Single Survey](#single-survey-activity)
11. [Question and Answer Objects](#question-types)
	- [Text](#question-text)
	- [Integer](#question-integer)
	- [Decimal](#question-decimal)
	- [Date](#question-date)
	- [Time](#question-time)
	- [Multiple Choice](#question-multiple-choice)
	- [Location](#question-location)
	- [Facility](#question-facility)





### <a name="list-surveys"></a> List Surveys

```
GET /api/surveys
```

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| fields | string | all fields | A comma-delimited list of survey properties that should be returned. |
| offset | integer | 0 | The offset of the result set. |
| limit | integer | 100 | Limits the number of results in the result set. |
| search | string OR regex |  | A string or regex to search on. |
| regex | boolean | false | Whether or not to parse the search param as a regex. |
| search_fields | string | survey_title | A comma-delimited list of survey properties that should be searched. |
| order_by | string | created_on:DESC | A comma-delimited list of survey properties with order direction, e.g. survey_title:ASC,created_on:DESC |
| draw | integer |  | If included in the request, the `draw` parameter will be returned in the response unaltered. |

*Note: All parameters are optional.*

If there is an error, return an **error** property as a string.

Example Response:
```json
{
    "error": "Some optional error message",
    "draw": 12345,
    "offset": 10,
    "limit": 10,
    "filtered_entries": 34839,
    "total_entries": 40629,
    "surveys": [
        {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "survey_metadata": {
                "location": {
                    "lon": 5.118915,
                    "lat": 7.353078
                },
                "author": "Abdizzle",
                "organization": "SEL"
            },
            "questions": [
                {
                    "sequence_number": 1,
                    "type_constraint_name": "integer",
                    "question_title": "integer question",
                    "question_id": "8bea838c-9373-410a-8510-cfda70469115",
                    "hint": "",
                    "logic": {
                        "allow_other": false,
                        "allow_dont_know": true,
                        "required": false
                    },
                    "allow_multiple": false,
                    "question_to_sequence_number": 2
                },
                {
                    "sequence_number": 2,
                    "type_constraint_name": "multiple_choice",
                    "question_title": "multiple choice question",
                    "question_id": "17d6976c-0bdc-4d72-accc-bfd8fc01be04",
                    "hint": "",
                    "logic": {
                        "allow_other": false,
                        "allow_dont_know": false,
                        "required": false
                    },
                    "allow_multiple": false,
                    "branches": [
                        {
                            "question_choice_id": "1feba851-c431-479a-8c38-c26c0128427b",
                            "to_question_id": "6510f6c5-860e-4b06-ae73-76af2b1ecea9",
                            "to_sequence_number": 3
                        },
                        {
                            "question_choice_id": "30d6aed1-ef7f-4db9-b4c1-fcbdfb99de2c",
                            "to_question_id": "3ba907ca-f80c-419f-a893-0745dae8e35c",
                            "to_sequence_number": 4
                        }
                    ],
                    "question_to_sequence_number": 3,
                    "choices": [
                        {
                            "choice": "choice 1",
                            "question_choice_id": "1feba851-c431-479a-8c38-c26c0128427b",
                            "choice_number": 1
                        },
                        {
                            "choice": "choice 2",
                            "question_choice_id": "30d6aed1-ef7f-4db9-b4c1-fcbdfb99de2c",
                            "choice_number": 2
                        }
                    ]
                },
                {
                    "sequence_number": 3,
                    "type_constraint_name": "decimal",
                    "question_title": "decimal question",
                    "question_id": "6510f6c5-860e-4b06-ae73-76af2b1ecea9",
                    "hint": "",
                    "logic": {
                        "allow_other": false,
                        "allow_dont_know": false,
                        "required": false
                    },
                    "allow_multiple": false,
                    "question_to_sequence_number": 4
                }
            ],
            "survey_title": "test_title",
            "survey_version": 0,
            "created_on": "2015-04-23T20:39:40.419031+00:00",
            "last_updated": "2015-04-23T20:39:40.419031+00:00"
        }
    ]
}
```

The minimal amount of `logic` is always `required`, `allow_other`, and `allow_dont_know`.

If a question's `type_constraint_name` is `multiple_choice` there will be a `choices` field like this:

```
"choices": [{
     "question_choice_id": "<Question_UUID>",
     "choice": "bananas",
     "choice_number": "0"
}]
```

If a question's `type_constraint_name` is `multiple_choice` there can be a `branches` field like this:

```
"branches": [{
     "question_choice_id": "<Question_Choice_UUID>",
     "to_question_id": "<Question_UUID>"
}]
```





### <a name="single-survey"></a> Get a Single Survey

```
GET /api/surveys/<Survey_UUID>
```

Example Response:
```json
{
    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
    "survey_metadata": {
        "location": {
            "lon": 5.118915,
            "lat": 7.353078
        },
        "author": "Abdizzle",
        "organization": "SEL"
    },
    "questions": [
        {
            "sequence_number": 1,
            "type_constraint_name": "integer",
            "question_title": "integer question",
            "question_id": "8bea838c-9373-410a-8510-cfda70469115",
            "hint": "",
            "logic": {
                "allow_other": false,
                "allow_dont_know": true,
                "required": false
            },
            "allow_multiple": false,
            "question_to_sequence_number": 2
        }
    ],
    "survey_title": "test_title",
    "survey_version": 0,
    "created_on": "2015-04-23T20:39:40.419031+00:00",
    "last_updated": "2015-04-23T20:39:40.419031+00:00"
}
```





### <a name="create-survey"></a> Create a New Survey

```
POST /api/surveys
```

Example Request Body:
```json
{
    "survey_title": "Another Test Survey",
    "email": "test_email",
    "survey_metadata": {
        "location": [
            5.118915,
            7.353078
        ]
    },
    "questions": [
        {
            "type_constraint_name": "integer",
            "question_title": "another integer question",
            "question_to_sequence_number": 2,
            "sequence_number": 1,
            "logic": {
                "required": false,
                "allow_other": false,
                "allow_dont_know": false
            },
            "allow_multiple": false,
            "hint": "",
            "choices": [],
            "branches": []
        },
        {
            "type_constraint_name": "note",
            "question_title": "another note",
            "question_to_sequence_number": -1,
            "sequence_number": 2,
            "logic": {
                "required": false,
                "allow_other": false,
                "allow_dont_know": false
            },
            "allow_multiple": false,
            "hint": "",
            "choices": [],
            "branches": []
        }
    ]
}
```

If you try to add a survey with a title that already exists for that user, a number surrounded by parentheses will be appended to the title. 

If a question's `type_constraint_name` is `multiple_choice`, the question's `choices` array should contain the possible answer values. E.g.:

```
"choices": ["choice 0", "choice 1", "choice 2"]
```

If you are creating a multiple choice question with branching, the question's `branches` array should contain the branching information (everything is 0-indexed). E.g.:

```
"branches": [{
	"choice_number": "0",
	"to_question_number": "1"
}]
```

If you want to make a question required, add `{"required": true}` in the `logic` field.

Example Response:
```
{
    "survey_id": "0b5da1ca-8181-4177-ad09-5773556a24d0",
    "last_updated": "2015-04-30T14:05:59.863833+00:00",
    "survey_title": "Another Test Survey",
    "survey_metadata": {
        "location": [
            5.118915,
            7.353078
        ]
    },
    "created_on": "2015-04-30T14:05:59.863833+00:00",
    "questions": [
        {
            "question_title": "another integer question",
            "logic": {
                "allow_other": false,
                "required": false,
                "allow_dont_know": false
            },
            "question_id": "795b02f7-95ef-47ed-97d0-315c6059de45",
            "hint": "",
            "type_constraint_name": "integer",
            "sequence_number": 1,
            "question_to_sequence_number": 2,
            "allow_multiple": false
        },
        {
            "question_title": "another note",
            "logic": {
                "allow_other": false,
                "required": false,
                "allow_dont_know": false
            },
            "question_id": "6c4c3fd0-6734-475e-a68b-40b8281f9a90",
            "hint": "",
            "type_constraint_name": "note",
            "sequence_number": 2,
            "question_to_sequence_number": -1,
            "allow_multiple": false
        }
    ],
    "survey_version": 0
}
```




### <a name="update-survey"></a> Update an Existing Survey
**TODO:** Figure out exactly how updates to a survey should work internally.

```
PUT /api/surveys/<Survey_UUID>
```

OR

```
POST /api/surveys/<Survey_UUID> with parameter _method=PUT
```

Example Request Body:
```json
{
    "survey_id": "0b5da1ca-8181-4177-ad09-5773556a24d0",
    "survey_title": "Another Test Survey",
    "survey_metadata": {
        "location": [
            42.98374,
            89.42452
        ]
    },
    "questions": [
        {
            "question_title": "another integer question",
            "logic": {
                "allow_other": false,
                "required": false,
                "allow_dont_know": false
            },
            "question_id": "795b02f7-95ef-47ed-97d0-315c6059de45",
            "hint": "",
            "type_constraint_name": "integer",
            "sequence_number": 1,
            "question_to_sequence_number": 2,
            "allow_multiple": false
        },
        {
            "question_title": "another note",
            "logic": {
                "allow_other": false,
                "required": false,
                "allow_dont_know": false
            },
            "question_id": "6c4c3fd0-6734-475e-a68b-40b8281f9a90",
            "hint": "",
            "type_constraint_name": "note",
            "sequence_number": 2,
            "question_to_sequence_number": -1,
            "allow_multiple": false
        }
    ],
    "survey_version": 0
}
```

Example Response:
```json
{
    "survey_id": "0b5da1ca-8181-4177-ad09-5773556a24d0",
    "last_updated": "2015-04-30T14:05:59.863833+00:00",
    "survey_title": "Another Test Survey",
    "survey_metadata": {
        "location": [
            5.118915,
            7.353078
        ]
    },
    "created_on": "2015-04-30T14:05:59.863833+00:00",
    "questions": [
        {
            "question_title": "another integer question",
            "logic": {
                "allow_other": false,
                "required": false,
                "allow_dont_know": false
            },
            "question_id": "795b02f7-95ef-47ed-97d0-315c6059de45",
            "hint": "",
            "type_constraint_name": "integer",
            "sequence_number": 1,
            "question_to_sequence_number": 2,
            "allow_multiple": false
        },
        {
            "question_title": "another note",
            "logic": {
                "allow_other": false,
                "required": false,
                "allow_dont_know": false
            },
            "question_id": "6c4c3fd0-6734-475e-a68b-40b8281f9a90",
            "hint": "",
            "type_constraint_name": "note",
            "sequence_number": 2,
            "question_to_sequence_number": -1,
            "allow_multiple": false
        }
    ],
    "survey_version": 0
}
```







### <a name="delete-survey"></a> Delete a Survey

```
DELETE /api/surveys/<Survey_UUID>
```

OR

```
POST /api/surveys/<Survey_UUID> with parameter _method=DELETE
```

Example Response:
```json
{
    "message": "Survey deleted"
}
```







### <a name="survey-submit"></a> Submit to a Survey

```
POST /api/surveys/<Survey_UUID>/submit
```
This endpoint allows for the creation of new submissions to a survey. It is equivalent to `POST /api/submissions`.

Example Request Body:
```json
{
    "submitter": "jwo",
    "submitter_email": "test_email",
    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
    "answers": [
        {
            "question_id": "8bea838c-9373-410a-8510-cfda70469115",
            "answer": 5,
            "answer_metadata": {},
            "is_type_exception": false
        },
        {
            "question_id": "17d6976c-0bdc-4d72-accc-bfd8fc01be04",
            "answer": "30d6aed1-ef7f-4db9-b4c1-fcbdfb99de2c",
            "answer_metadata": {},
            "is_type_exception": false
        },
        {
            "question_id": "f80313a4-87a4-4502-886a-c37fc7287b0a",
            "answer": {
                "lat": 40.809146399999996,
                "lon": -73.9596241
            },
            "answer_metadata": {},
            "is_type_exception": false
        }
    ],
    "save_time": "2015-04-30T14:43:33.443Z"
}
```

Example Response:
```json
{
    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
    "submitter_email": "test_email",
    "save_time": "2015-04-30T14:43:33.443000+00:00",
    "submission_time": "2015-04-30T14:43:35.179448+00:00",
    "submission_id": "0ea18cfa-e839-4897-a312-e7fde0420a60",
    "answers": [
        {
            "answer": 5,
            "question_title": "integer question",
            "question_id": "8bea838c-9373-410a-8510-cfda70469115",
            "answer_id": "67147eae-adb8-4ad5-98b9-27955beea372",
            "choice_number": null,
            "sequence_number": 1,
            "answer_metadata": {},
            "type_constraint_name": "integer",
            "choice": null,
            "is_type_exception": false
        },
        {
            "answer": "30d6aed1-ef7f-4db9-b4c1-fcbdfb99de2c",
            "question_title": "multiple choice question",
            "answer_choice_metadata": {},
            "question_id": "17d6976c-0bdc-4d72-accc-bfd8fc01be04",
            "answer_id": "ca958d8f-8e99-4829-a599-c6c7656a7654",
            "sequence_number": 2,
            "choice_number": 2,
            "type_constraint_name": "multiple_choice",
            "choice": "choice 2",
            "is_type_exception": false
        },
        {
            "answer": [
                -73.9596241,
                40.8091464
            ],
            "question_title": "location question",
            "question_id": "f80313a4-87a4-4502-886a-c37fc7287b0a",
            "answer_id": "5dce47bd-4fd8-483e-aede-9231f1c14e5b",
            "choice_number": null,
            "sequence_number": 6,
            "answer_metadata": {},
            "type_constraint_name": "location",
            "choice": null,
            "is_type_exception": false
        }
    ],
    "submitter": "jwo"
}
```







### <a name="survey-submissions"></a> List Submissions to a Survey

```
GET /api/surveys/<Survey_UUID>/submissions
```

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| fields | string | all fields | A comma-delimited list of submission properties that should be returned. |
| offset | integer | 0 | The offset of the result set. |
| limit | integer | 100 | Limits the number of results in the result set. |
| search | string OR regex |  | A string or regex to search on. |
| regex | boolean | false | Whether or not to parse the search param as a regex. |
| search_fields | string |  | A comma-delimited list of submission properties that should be searched. |
| order_by | string | created_on:DESC | A comma-delimited list of submission properties with order direction, e.g. survey_title:ASC,created_on:DESC |
| draw | integer |  | If included in the request, the `draw` parameter will be returned in the response unaltered. |

*Note: All parameters are optional.*

If there is an error, return an **error** property as a string.

Example Response:
```json
{
    "error": "Some optional error message, if there is an error.",
    "draw": 12345,
    "offset": 10,
    "limit": 10,
    "filtered_entries": 34839,
    "total_entries": 40629,
    "submissions": [
        {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "survey_title": "test_title",
            "submitter": "jwo",
            "submission_id": "2fdae261-c5be-4c0b-8464-09f74708e5af",
            "submission_time": "2015-04-28T15:52:05.456000+00:00",
            "answers": [
                {
                    "is_type_exception": false,
                    "choice": null,
                    "type_constraint_name": "integer",
                    "question_title": "integer question",
                    "question_id": "8bea838c-9373-410a-8510-cfda70469115",
                    "sequence_number": 1,
                    "answer": 5,
                    "choice_number": null,
                    "answer_metadata": {},
                    "answer_id": "01207c54-e520-44c5-8ea7-d128c50bd8bb"
                },
                {
                    "is_type_exception": false,
                    "choice": null,
                    "type_constraint_name": "location",
                    "question_title": "location question",
                    "question_id": "f80313a4-87a4-4502-886a-c37fc7287b0a",
                    "sequence_number": 6,
                    "answer": [
                        -73.9598084,
                        40.8093621
                    ],
                    "choice_number": null,
                    "answer_metadata": {},
                    "answer_id": "b9f3803a-2aa8-4120-81ad-4f8e3839dc8f"
                }
            ],
            "submitter_email": "anon@anon.org",
            "save_time": "2015-04-28T15:52:03.673000+00:00"
        }
    ]
}
```

### <a name="survey-stats"></a> Get Stats for a Single Survey

```
GET /api/surveys/<Survey_UUID>/stats
```

Example Response:
```json
{
    "latest_submission_time": "2015-04-28T15:52:05.456000+00:00",
    "created_on": "2015-04-23T20:39:40.419031+00:00",
    "earliest_submission_time": "2015-04-23T20:39:44.632526+00:00",
    "num_submissions": 8
}
```

### <a name="all-surveys-activity"></a> Get Submission Activity for All Surveys

```
GET /api/surveys/activity
```
Retrieve the number of submissions per day accross all surveys, ordered by date:ASC.

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| days | integer | 30 | The number of days in the past for which activity should be returned. |

*Note: All parameters are optional.*

Example Response:
```json
{
    "activity": [
        {
            "date": 2015-04-23,
            "num_submissions": 20
        },
        {
            "date": 2015-04-24,
            "num_submissions": 21
        }
    ]
}
```

### <a name="single-survey-activity"></a> Get Submission Activity for a Single Survey

```
GET /api/surveys/<Survey_UUID>/activity
```
Retrieve the number of submissions per day for a single surveys, ordered by date:ASC.

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| days | integer | 30 | The number of days in the past for which activity should be returned. |

*Note: All parameters are optional.*

Example Response:
```json
{
    "activity": [
        {
            "date": 2015-04-23,
            "num_submissions": 20
        },
        {
            "date": 2015-04-24,
            "num_submissions": 21
        }
    ]
}
```


### <a name="question-types"></a> Question and Answer Objects

Below are examples of question and answer objects for each available question type (i.e. `type_constraint_name`).

The `allow_dont_know` logic property indicates that this question should offer an "I don't know the answer" option on the user interface. It is functionally equivilant to the `allow_other` option, but operationally allows for a distinction between a known and unknown answer, and gives enumerators the opportunity to add additional information.

#### <a name="question-text"></a> Text
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Description",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "text",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "text",
    "answer": "Howdy!",
    "choice": null,
    "choice_number: null,
    "is_type_exception": false
}
```


#### <a name="question-integer"></a> Integer
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Number from 5 to 10",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "integer",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "integer",
    "answer": 6,
    "choice": null,
    "choice_number: null,
    "is_type_exception": false
}
```


#### <a name="question-decimal"></a> Decimal
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Ratio of teachers to kids",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "decimal",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "decimal",
    "answer": 0.047,
    "choice": null,
    "choice_number: null,
    "is_type_exception": false
}
```


#### <a name="question-date"></a> Date
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Date",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "date",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "date",
    "answer": "1970-01-15",
    "choice": null,
    "choice_number: null,
    "is_type_exception": false
}
```

The date should be given as `"YYYY-MM-DD"` - year, month, date


#### <a name="question-time"></a> Time (with timezone)
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Time",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "time",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "time",
    "answer": "12:59:00-04:00",
    "choice": null,
    "choice_number: null,
    "is_type_exception": false
}
```

The time should be given as `"HH:MM:SS{+,-}UTC"` - hour, minute, second, UTC offset. See http://en.wikipedia.org/wiki/ISO_8601

If seconds are not provided (`HH:MM{+,-}UTC`, `12:59-04:00`), the default is 0. The response answer will look like `HH:MM:00{+,-}UTC`

If the UTC offset is not provided, I believe the default is the time zone of the database... which is probably not what you want. At all.


#### <a name="question-multiple-choice"></a> Multiple Choice
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Pick one",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,    
    "type_constraint_name": "multiple_choice",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [{
                     "question_choice_id": "<Question_Choice_UUID>",
                     "choice": "bananas"
                },
                {
                     "question_choice_id": "<Question_Choice_UUID>",
                     "choice": "apples"
                },
                {
                     "question_choice_id": "<Question_Choice_UUID>",
                     "choice": "pears"
                }]
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "multiple_choice",
    "question_choice_id": "<Question_Choice_UUID>",
    "choice": "bananas",
    "choice_number": 0,
    "is_type_exception": false
}
```

If `allow_other` is true, an answer can either be a `question_choice_id` (if `is_type_exception` is false) or some other value (if `is_type_exception` is true).


#### <a name="question-location"></a> Location
```
// Question
{
    "question_id": "<Question_UUID>",
    "question_title": "Location",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "location",
    "logic": {
        "required": false,
        "allow_other": false,
        "allow_dont_know": true
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<Answer_UUID>",
    "question_id": "<Question_UUID>",
    "type_constraint_name": "location",
    "answer": [<longitude>, <latitude>],
    "choice": null,
    "choice_number: null,
    "is_type_exception": false
}
```

#### <a name="question-facility"></a> Facility
**TODO:** Add the question/answer for Facility-type questions.