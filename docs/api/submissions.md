## Dokomo REST API

# Submissions

1. [List Submissions](#list-submissions)
2. [Get a Single Submission](#single-submission)
3. [Create a New Submission](#create-submission)
4. [Create Multiple Submissions (Batch Creation)](#create-batch)
5. [Delete a Submission](#delete-submission)


### <a name="list-submissions"></a> List Submissions

```
GET /api/submissions
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

### <a name="single-submission"></a> Get a Single Submission

```
/api/submissions/<Submission_UUID>
```

Example Response:
```json
{
    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
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
```

### <a name="create-submission"></a> Create a New Submission

```
POST /api/submissions
```
This endpoint is equivalent to `POST /api/surveys/<Survey_UUID>/submit`.

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

### <a name="create-batch"></a> Create Multiple Submissions (Batch Creation)

```
POST /api/submissions/batch
```

This API endpoint allows for the creation of multiple submissions with a single request. The response contains a list of the new Submission UUIDs.

Example Request Body:
```json
{
    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
    "submissions": [
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
            "save_time": "2015-04-30T11:43:33.443Z"
        },
        {
            "submitter": "jwo",
            "submitter_email": "test_email",
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "answers": [
                {
                    "question_id": "8bea838c-9373-410a-8510-cfda70469115",
                    "answer": 10,
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
                        "lat": 41.809146399999996,
                        "lon": -76.9596241
                    },
                    "answer_metadata": {},
                    "is_type_exception": false
                }
            ],
            "save_time": "2015-04-30T12:43:33.443Z"
        }
    ]
}
```

Example Response:
```json
{
    "result": [
        "cb6ab0fb-d6aa-48ae-9bcf-87693a14d8d8",
        "220dd79f-96b8-42c9-818d-5d27d26eca03"
    ]
}
```


### <a name="delete-submission"></a> Delete Submission

```
DELETE /api/submissions/<Submission_UUID>
```

OR

```
POST /api/submissions/<Submission_UUID> with parameter _method=DELETE
```

Example Response:
```json
{
    "message": "Submission deleted"
}
```