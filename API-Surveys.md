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





### <a name="list-surveys"></a> List Surveys

```
GET /api/v0/surveys
```

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| offset | integer | 0 | The offset of the result set. |
| limit | integer | 100 | Limits the number of results in the result set. |
| order_by | string | created_on:DESC | A comma-delimited list of survey properties with order direction, e.g. survey_title:ASC,created_on:DESC |
| draw | integer |  | If included in the request, the `draw` parameter will be returned in the response unaltered. |

*Note: All parameters are optional.*

If there is an error, the response will contain a single `error` property containing the error message.

#### Example Response:
```json
{
    "draw": 12345,
    "offset": 10,
    "limit": 10,
    "surveys": [
        {
            "id": "8d0d6d6e-6519-4793-8575-d7ababad7dcb",
            "deleted": false,
            "title": {
                "English": "integer_survey"
            },
            "default_language": "English",
            "survey_type": "public",
            "version": 1,
            "creator_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
            "creator_name": "test_user",
            "metadata": {},
            "created_on": "2015-06-30T15:29:34.566835+00:00",
            "last_update_time": "2015-06-30T15:29:34.566835+00:00",
            "nodes": [
                {
                    "title": {
                        "English": "integer_node"
                    },
                    "hint": {
                        "English": ""
                    },
                    "allow_multiple": false,
                    "allow_other": false,
                    "type_constraint": "integer",
                    "logic": {},
                    "last_update_time": "2015-06-30T15:29:34.566835+00:00",
                    "node_id": "447e2767-c5bd-43d3-9b87-811dde48b1a9",
                    "id": "958bd0f4-19a3-4644-bdfa-da17b1de1b27",
                    "deleted": false,
                    "required": false,
                    "allow_dont_know": false
                }
            ]
        },
        {
            "id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "deleted": false,
            "title": {
                "English": "single_survey"
            },
            "default_language": "English",
            "survey_type": "public",
            "version": 1,
            "creator_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
            "creator_name": "test_user",
            "metadata": {},
            "created_on": "2015-06-30T15:29:34.566835+00:00",
            "last_update_time": "2015-06-30T15:29:34.566835+00:00",
            "nodes": [
                {
                    "title": {
                        "English": "integer node"
                    },
                    "hint": {
                        "English": ""
                    },
                    "allow_multiple": false,
                    "allow_other": false,
                    "type_constraint": "integer",
                    "logic": {},
                    "last_update_time": "2015-06-30T15:29:34.566835+00:00",
                    "node_id": "60e56824-910c-47aa-b5c0-71493277b43f",
                    "id": "e370cb1c-41f2-49e1-b861-295858f30f9e",
                    "deleted": false,
                    "required": false,
                    "allow_dont_know": false,
                    "sub_surveys": [
                        {
                            "deleted": false,
                            "buckets": [
                                "[2,3)"
                            ],
                            "repeatable": false,
                            "nodes": [
                                {
                                    "title": {
                                        "English": "decimal node"
                                    },
                                    "hint": {
                                        "English": ""
                                    },
                                    "allow_multiple": false,
                                    "allow_other": false,
                                    "type_constraint": "decimal",
                                    "logic": {},
                                    "last_update_time": "2015-06-30T15:29:34.566835+00:00",
                                    "node_id": "c1154cd3-38d5-4bce-9eb7-ffaf57eae9bf",
                                    "id": "d8aa7c16-b4eb-4be3-ad97-2d3b4539d974",
                                    "deleted": false,
                                    "required": false,
                                    "allow_dont_know": false,
                                    "sub_surveys": [
                                        {
                                            "deleted": false,
                                            "buckets": [
                                                "(1.3,2.3]"
                                            ],
                                            "repeatable": false,
                                            "nodes": []
                                        }
                                    ]
                                },
                                {
                                    "title": {
                                        "English": "integer node"
                                    },
                                    "hint": {
                                        "English": ""
                                    },
                                    "allow_multiple": false,
                                    "allow_other": false,
                                    "type_constraint": "integer",
                                    "logic": {},
                                    "last_update_time": "2015-06-30T15:29:34.566835+00:00",
                                    "node_id": "a812eb34-b3fb-40bb-b7e2-20332acf83dd",
                                    "id": "909f013d-7a9e-41b9-a943-88c96a4c3399",
                                    "deleted": false,
                                    "required": false,
                                    "allow_dont_know": false,
                                    "sub_surveys": [
                                        {
                                            "deleted": false,
                                            "buckets": [
                                                "[2,3)"
                                            ],
                                            "repeatable": false,
                                            "nodes": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

Within a `survey` object, each `node` represents a question. A `node` can have an array of `sub_surveys`, in which each sub survey is a branch of survey nodes stemming from the question `node`. Each `sub_survey` contains an array of `buckets` which defines the branching rules which determine when the `sub_survey` is presented while conducting a survey.

If a question's `type_constraint` is `multiple_choice` there will be a `choices` field:

```
"choices": [
    {
        "choice_id": "5325e828-0b2b-47a3-95a7-c8fa7f7f8c77",
        "choice_text": {
            "English": "first choice"
        }
    },
    {
        "choice_id": "fcfb0e34-2de2-4cd4-bc10-615ba23e6619",
        "choice_text": {
            "English": "second choice"
        }
    }
]
```





### <a name="single-survey"></a> Get a Single Survey

```
GET /api/v0/surveys/<Survey_UUID>
```

#### Example Response:
```json
{
    "id": "ff91cce7-3049-4935-adf2-aba64cf48efd",
    "deleted": false,
    "title": {
        "English": "timestamp_survey"
    },
    "default_language": "English",
    "survey_type": "public",
    "version": 1,
    "creator_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
    "creator_name": "test_user",
    "metadata": {},
    "created_on": "2015-07-01T18:17:18.984452+00:00",
    "last_update_time": "2015-07-01T18:17:18.984452+00:00",
    "nodes": [
        {
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "timestamp_node"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "timestamp",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "node_id": "8e6e6905-3d18-4230-87ce-435fd074d421",
            "id": "2a356dfc-2a87-4abe-9633-e524e00b5c15",
            "required": false,
            "allow_dont_know": false
        }
    ]
}
```





### <a name="create-survey"></a> Create a New Survey

```
POST /api/v0/surveys
```

When a survey is created via the API it is associated with the currently authenticated user.

Surveys are logically separate from the nodes (i.e. questions) they contain. A survey can be created passing a list of
node objects containing existing node ids, or by passing full node definitions which will be used to generate a new node in the process of creating the survey.

#### Example Request Body, using existing nodes:
```json
{
    "title": {
        "English": "Another Survey"
    },
    "default_language": "English",
    "survey_type": "public",
    "metadata": {},
    "nodes": [
        {
            "id": "2a356dfc-2a87-4abe-9633-e524e00b5c15"
        },
        {
            "id": "b02a6dfc-2a87-4abe-9633-e524e00b5c14"
        }
    ]
}
```

#### Example Request Body, using node definition:
```json
{
    "title": {
        "English": "Another Survey"
    },
    "default_language": "English",
    "survey_type": "public",
    "metadata": {},
    "nodes": [
        {
            "title": {"English": "test_time_node"},
            "hint": {
                "English": ""
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": "time",
            "logic": {},
            "deleted": False
        }
    ]
}
```

#### Example Response:
```
{
    "id": "ff91cce7-3049-4935-adf2-aba64cf48efd",
    "deleted": false,
    "title": {
        "English": "Another Survey"
    },
    "default_language": "English",
    "survey_type": "public",
    "version": 1,
    "creator_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
    "creator_name": "test_user",
    "metadata": {},
    "created_on": "2015-07-01T18:17:18.984452+00:00",
    "last_update_time": "2015-07-01T18:17:18.984452+00:00",
    "nodes": [
        {
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "timestamp_node"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "timestamp",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "node_id": "2a356dfc-2a87-4abe-9633-e524e00b5c15",
            "id": "8e6e6905-3d18-4230-87ce-435fd074d421",
            "required": false,
            "allow_dont_know": false
        },
        {
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "timestamp_node"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "timestamp",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "node_id": "b02a6dfc-2a87-4abe-9633-e524e00b5c14",
            "id": "afd9dfc-2a87-4abe-9633-e524e00b5c15",
            "required": false,
            "allow_dont_know": false
        }
    ]
}
```




### <a name="update-survey"></a> Update an Existing Survey
**TODO:** Figure out exactly how updates to a survey should work internally.

```
PUT /api/v0/surveys/<Survey_UUID>
```


Example Request Body:
```json
{
    "id": "ff91cce7-3049-4935-adf2-aba64cf48efd",
    "deleted": false,
    "title": {
        "English": "Another Survey"
    },
    "default_language": "English",
    "survey_type": "public",
    "version": 1,
    "creator_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
    "creator_name": "test_user",
    "metadata": {},
    "created_on": "2015-07-01T18:17:18.984452+00:00",
    "last_update_time": "2015-07-01T18:17:18.984452+00:00",
    "nodes": [
        {
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "timestamp_node"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "timestamp",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "node_id": "2a356dfc-2a87-4abe-9633-e524e00b5c15",
            "id": "8e6e6905-3d18-4230-87ce-435fd074d421",
            "required": false,
            "allow_dont_know": false
        }
    ]
}
```

#### Example Response:
```json
{
    "id": "ff91cce7-3049-4935-adf2-aba64cf48efd",
    "deleted": false,
    "title": {
        "English": "Another Survey"
    },
    "default_language": "English",
    "survey_type": "public",
    "version": 1,
    "creator_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
    "creator_name": "test_user",
    "metadata": {},
    "created_on": "2015-07-01T18:17:18.984452+00:00",
    "last_update_time": "2015-07-01T18:17:18.984452+00:00",
    "nodes": [
        {
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "timestamp_node"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "timestamp",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "node_id": "2a356dfc-2a87-4abe-9633-e524e00b5c15",
            "id": "8e6e6905-3d18-4230-87ce-435fd074d421",
            "required": false,
            "allow_dont_know": false
        }
    ]
}
```







### <a name="delete-survey"></a> Delete a Survey

```
DELETE /api/v0/surveys/<Survey_UUID>
```

Delete requests have no response payload. A successful deletion will respond with an empty `204` No Content status code.

**Note**: Deletions are non-destructive; data is simply marked as deleted, and will no longer appear in standard queries.





### <a name="survey-submit"></a> Submit to a Survey

```
POST /api/v0/surveys/<Survey_UUID>/submit
```
This endpoint allows for the creation of new submissions to a survey. It is equivalent to `POST /api/v0/submissions`.

A submission can have one of two `submission_type` values, either `unauthenticated` or `authenticated`. If a survey was created with `survey_type` = `enumerator_only`, then only `authenticated` submissions will be allowed. A survey created with `survey_type` = `public` will allow both `unauthenticated` and `authenticated` submissions.

Example Request Body:
```json
{
    "submitter_name": "regular",
    "submission_type": "unauthenticated",
    "answers": [
        {
            "survey_node_id": "60e56824-910c-47aa-b5c0-71493277b43f",
            "type_constraint": "integer",
            "answer": 3
        }
    ]
}
```

#### Example Response:
```json
{
    "id": "8a4d237e-acb7-4696-a4fe-ce6322681483",
    "deleted": false,
    "survey_id": "cd7b041c-f2bf-4aac-b772-d63b6cd24cbc",
    "save_time": "2015-07-01T18:58:36.862880+00:00",
    "submission_time": "2015-07-01T18:58:36.862880+00:00",
    "last_update_time": "2015-07-01T18:58:36.862880+00:00",
    "submitter_name": "regular",
    "submitter_email": "",
    "answers": [
        {
            "response_type": "answer",
            "response": 3
        }
    ]
}
```







### <a name="survey-submissions"></a> List Submissions to a Survey

```
GET /api/v0/surveys/<Survey_UUID>/submissions
```

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| offset | integer | 0 | The offset of the result set. |
| limit | integer | 100 | Limits the number of results in the result set. |
| order_by | string | created_on:DESC | A comma-delimited list of submission properties with order direction, e.g. survey_title:ASC,created_on:DESC |
| draw | integer |  | If included in the request, the `draw` parameter will be returned in the response unaltered. |

*Note: All parameters are optional.*

If there is an error, the response will contain a single `error` property containing the error message.

#### Example Response:
```json
{
    "survey_id": "cd7b041c-f2bf-4aac-b772-d63b6cd24cbc",
    "draw": 12345,
    "offset": 10,
    "limit": 10,
    "submissions": [
        {
            "id": "e9f40635-c114-4f9f-bac5-657ef21692a3",
            "deleted": false,
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "save_time": "2015-07-01T18:17:18.984452+00:00",
            "submission_time": "2015-03-24T00:00:00+00:00",
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "submitter_name": "regular",
            "submitter_email": "",
            "answers": []
        },
        {
            "id": "8a4d237e-acb7-4696-a4fe-ce6322681483",
            "deleted": false,
            "survey_id": "cd7b041c-f2bf-4aac-b772-d63b6cd24cbc",
            "save_time": "2015-07-01T18:58:36.862880+00:00",
            "submission_time": "2015-07-01T18:58:36.862880+00:00",
            "last_update_time": "2015-07-01T18:58:36.862880+00:00",
            "submitter_name": "regular",
            "submitter_email": "",
            "answers": [
                {
                    "response_type": "answer",
                    "response": 3
                }
            ]
        }
    ]
}
```

### <a name="survey-stats"></a> Get Stats for a Single Survey

```
GET /api/v0/surveys/<Survey_UUID>/stats
```

#### Example Response:
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
GET /api/v0/surveys/activity
```
Retrieve the number of submissions per day accross all surveys, ordered by date:ASC.

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| days | integer | 30 | The number of days in the past for which activity should be returned. |

*Note: All parameters are optional.*

#### Example Response:
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
GET /api/v0/surveys/<Survey_UUID>/activity
```
Retrieve the number of submissions per day for a single surveys, ordered by date:ASC.

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| days | integer | 30 | The number of days in the past for which activity should be returned. |

*Note: All parameters are optional.*

#### Example Response:
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