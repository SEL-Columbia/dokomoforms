# Submissions

1. [List Submissions](#list-submissions)
2. [Get a Single Submission](#single-submission)
3. [Create a New Submission](#create-submission)
4. [Delete a Submission](#delete-submission)


### <a name="list-submissions"></a> List Submissions

```
GET /api/v0/submissions
```
#### Implemented Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| offset | integer | 0 | The offset of the result set. |
| limit | integer |  | Limits the number of results in the result set. |
| draw | integer |  | If included in the request, the `draw` parameter will be returned in the response unaltered. |

#### Planned Parameters (Not Implemented)
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| fields | string | all fields | A comma-delimited list of submission properties that should be returned. |
| search | string OR regex |  | A string or regex to search on. |
| regex | boolean | false | Whether or not to parse the search param as a regex. |
| search_fields | string | title | A comma-delimited list of submission properties that should be searched. |
| order_by | string | created_on:DESC | A comma-delimited list of submission properties with order direction, e.g. title:ASC,created_on:DESC |
*Note: All parameters are optional.*

If there is an error, the response will contain a single `error` property containing the error message.

#### Example Response:
```json
{
    "limit": 4,
    "offset": 5,
    "submissions": [
        {
            "id": "68186c3e-ebdc-4d76-9d52-a917d2e088b7",
            "deleted": false,
            "survey_id": "ff91cce7-3049-4935-adf2-aba64cf48efd",
            "save_time": "2015-07-01T18:17:18.984452+00:00",
            "submission_time": "2015-07-01T18:17:18.984452+00:00",
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "submitter_name": "regular",
            "submitter_email": "",
            "answers": [
                {
                    "response_type": "answer",
                    "response": 321
                }
            ]
        },
        {
            "id": "4d8c0d94-f175-4775-b34d-d321902b95c7",
            "deleted": false,
            "survey_id": "157d2002-ba3a-4b9f-b6d4-91997517f40e",
            "save_time": "2015-07-01T18:17:18.984452+00:00",
            "submission_time": "2015-07-01T18:17:18.984452+00:00",
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "submitter_name": "regular",
            "submitter_email": "",
            "answers": [
                {
                    "response_type": "answer",
                    "response": 1
                }
            ]
        },
        {
            "id": "43f4eb0d-4133-478c-bd15-7dbe0eeeabc3",
            "deleted": false,
            "survey_id": "c679c345-b0e1-47ee-9315-f16b7ca14ce3",
            "save_time": "2015-07-01T18:17:18.984452+00:00",
            "submission_time": "2015-07-01T18:17:18.984452+00:00",
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
            "submitter_name": "regular",
            "submitter_email": "",
            "answers": [
                {
                    "response_type": "answer",
                    "response": 5
                }
            ]
        },
        {
            "id": "51c52057-4706-495e-a6ca-9270da209e0d",
            "deleted": false,
            "survey_id": "19c0ca06-ef73-44c3-94f9-b8d8860bdc61",
            "save_time": "2015-07-01T18:17:18.984452+00:00",
            "submission_time": "2015-07-01T18:17:18.984452+00:00",
            "last_update_time": "2015-07-01T18:17:18.984452+00:00",
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

### <a name="single-submission"></a> Get a Single Submission

```
/api/v0/submissions/<Submission_UUID>
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

### <a name="create-submission"></a> Create a New Submission

```
POST /api/v0/submissions
```
This endpoint is equivalent to `POST /api/v0/surveys/<Survey_UUID>/submit`, except that in this case the `survey_id` is required in the body.

A submission can have one of two `submission_type` values, either `unauthenticated` or `authenticated`. If a survey was created with `survey_type` = `enumerator_only`, then only `authenticated` submissions will be allowed. A survey created with `survey_type` = `public` will allow both `unauthenticated` and `authenticated` submissions.

#### Example Request Body:
```json
{
    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
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


### <a name="delete-submission"></a> Delete Submission

```
DELETE /api/v0/submissions/<Submission_UUID>
```

Delete requests have no response payload. A successful deletion will respond with an empty `204` No Content status code.

**Note**: Deletions are non-destructive; data is simply marked as deleted, and will no longer appear in standard queries.
