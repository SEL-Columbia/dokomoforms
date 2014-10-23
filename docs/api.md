Dokomoform's REST JSON API.

## Authentication

Done through normal login + session cookies. Later we may add in HTTP Basic Auth to support other clients.

## Requests, Responses, and Errors

The API will support the **GET**, **POST**, and **DELETE** HTTP methods.

For IE < 9 compatibility purposes, **DELETE** requests can also be emulated by POSTing with the `_method=delete`.

POST requests should include the **data** argument with the value as a JSON object.

The server will always return a JSON object as a response.

On error, the server will respond with the corresponding HTTP response code.


## Surveys

### List Surveys

`GET /surveys`

Response:
```
[
    {
        "survey_id": "<UUID>",
        "title": "Batcave inventory",
        "questions": [{
            "question_id": "<UUID>",
            "title": "Batmobile jet fuel reserves (L)",
            "hint": "",
            "required": false,
            "sequence_number": 1,
            "allow_multiple": false,
            "type_constraint_name": "integer",
            "logical_constraint_name": ""
        }]
    }
]
```

### Get Survey
`GET /surveys/<UUID>`

Response:
```
{
    "survey_id": "<UUID>",
    "title": "Batcave inventory",
    "questions": [{
        "question_id": "<UUID>",
        "title": "Batmobile jet fuel reserves (L)",
        "hint": "",
        "required": false,
        "sequence_number": 1,
        "allow_multiple": false,
        "type_constraint_name": "integer",
        "logical_constraint_name": ""
    }]
}
```


### Create Survey
`POST /surveys`

Request data:
```
{
    "title": "Batcave inventory",
    "questions": [{
        "title": "Batmobile jet fuel reserves (L)",
        "type_constraint_name": "integer",
        "sequence_number": null,
        "hint": null,
        "required": null,
        "allow_multiple": null,
        "logical_constraint_name": null
    }]
}
```

Response:
```
{
    "survey_id": "<UUID>",
    "title": "Batcave inventory",
    "questions": [{
        "question_id": "<UUID>"
        "title": "Batmobile jet fuel reserves (L)",
        "type_constraint_name": "integer",
        "sequence_number": 1,
        "hint": "",
        "required": false,
        "allow_multiple": false,
        "logical_constraint_name": ""
    }]
}
```


### Update Survey
`POST /surveys/<UUID>`

Request data:
```
{
    "survey_id": "<UUID>",
    "title": "Batcave inventory v2",
    "questions": [
        {
            "question_id": "<UUID>"
            "title": "Update this question (has an id)",
        },
        {
            "title": "Add a new question (no id)",
            "type_constraint_name": "text",
            "sequence_number": null,
            "hint": null,
            "required": null,
            "allow_multiple": null,
            "logical_constraint_name": null
        }
    ]
}
```

Response:
```
{
    "survey_id": "<UUID>",
    "title": "Batcave inventory v2",
    "questions": [
        {
            "question_id": "<UUID>"
            "title": "Update this question (has an id)",
            "type_constraint_name": "integer",
            "sequence_number": 1,
            "hint": "",
            "required": false,
            "allow_multiple": false,
            "logical_constraint_name": ""
        },
        {
            "question_id": "<UUID>",
            "title": "Add a new question (no id)",
            "type_constraint_name": "text",
            "sequence_number": 2,
            "hint": "",
            "required": false,
            "allow_multiple": false,
            "logical_constraint_name": ""
        }
    ]
}
```

### Delete Survey
`DELETE /surveys/<UUID>`

or

`POST /surveys/<UUID>` with argument `_method=DELETE`


Response:
```
{
    "message": "Survey deleted"
}
```


## Survey Submissions

### List submissions
`GET /surveys/<UUID>/submissions`

Response:
```
[
    {
        "submission_id": "<UUID>",
        "survey_id": "<UUID>",
        "submitter": "<submitter>",
        "submission_time": "<ISO time>",
        "answers": [{
            "answer_id": "<UUID>",
            "question_id": "<UUID>",
            "type_constraint_name": "integer",
            "answer": 6
        }]
    }
]
```


### Get Submission
`GET /submissions/<UUID>`

Response:
```
{
    "submission_id": "<UUID>",
    "survey_id": "<UUID>",
    "submitter": "<submitter>",
    "submission_time": "<ISO time>",
    "answers": [{
        "answer_id": "<UUID>",
        "question_id": "<UUID>",
        "type_constraint_name": "integer",
        "answer": 6
    }]
}
```

### New Submission
`POST /submissions`

Request:
```
{
    "survey_id": "<UUID>",
    "submitter": "<submitter>",
    "answers": [{
        "question_id": "<UUID>",
        "answer": 6
    }]
}
```

Response:
```
{
    "submission_id": "<UUID>",
    "survey_id": "<UUID>",
    "submitter": "<submitter>",
    "submission_time": "<ISO time>",
    "answers": [{
        "answer_id": "<UUID>",
        "question_id": "<UUID>",
        "type_constraint_name": "integer",
        "answer": 6
    }]
}
```

### Delete Submission
`DELETE /submissions/<UUID>`

or

`POST /submissions/<UUID>` with argument `_method=DELETE`

```
{
    "message": "Submission deleted"
}
```


## Question & Answer Objects

### Location
```
// Question
{
    "question_id": "<UUID>",
    "title": "Location",
    "hint": "",
    "required": false,
    "sequence_number": 1,
    "allow_multiple": false,
    "type_constraint_name": "location",
    "logical_constraint_name": ""
}

// Answer
{
    "answer_id": "<UUID>",
    "answer": [<longitude>, <latitude>]
}
```


### Integer
Need to consider what exactly to do about logical constraints.
```
// Question
{
    "question_id": "<UUID>",
    "title": "Number from 5 to 10",
    "hint": "",
    "required": false,
    "sequence_number": 1,
    "allow_multiple": false,
    "type_constraint_name": "integer",
    "logical_constraint_name": ""
}

// Answer
{
    "answer_id": "<UUID>",
    "answer": 6
}
```

### Text
```
// Question
{
    "question_id": "<UUID>",
    "title": "Description",
    "hint": "",
    "required": false,
    "sequence_number": 1,
    "allow_multiple": false,
    "type_constraint_name": "text",
    "logical_constraint_name": ""
}

// Answer
{
    "answer_id": "<UUID>",
    "answer": "Howdy!"
}
```


### Multiple Choice
Still need to figure out what to do about these in the code.
```
// Question
{
    "id": "<UUID>",
    "label": "Pick one",
    "type": "choice",
    "choices": ["Banana", "Apple", "Pear"]
}

// Answer
{
    "id": "<UUID>",
    "answer": "Banana"
}
```

