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
            "sequence_number": 0,
            "allow_multiple": false,
            "type_constraint_name": "integer",
            "logic": {}
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
        "sequence_number": 0,
        "allow_multiple": false,
        "type_constraint_name": "integer",
        "logic": {}
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
        "logic": null
    }]
}
```

If `type_constraint_name` is `multiple_choice` or `multiple_choice_with_other`, the question dict should also contain

```
"choices": ["choice 0", "choice 1", "choice 2"]
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
        "sequence_number": 0,
        "hint": "",
        "required": false,
        "allow_multiple": false,
        "logic": "{}"
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
            "logic": null
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
            "sequence_number": 0,
            "hint": "",
            "required": false,
            "allow_multiple": false,
            "logic": {}
        },
        {
            "question_id": "<UUID>",
            "title": "Add a new question (no id)",
            "type_constraint_name": "text",
            "sequence_number": 1,
            "hint": "",
            "required": false,
            "allow_multiple": false,
            "logic": {}
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

If `type_constraint_name` is `multiple_choice` or `multiple_choice_with_other`, an entry in the `answers` list will look like this:

```
"answer_id": "<UUID>",
"question_id": "<UUID>",
"type_constraint_name": "multiple_choice",
"question_choice_id: "<UUID>",
"choice": "bananas",
"choice_number": 0
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

If the question to be answered is a `multiple_choice` or `multiple_choice_with_other` question, `answer` can be `question_choice_id` instead.

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
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "location",
    "logic": {}
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "location",
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
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "integer",
    "logic": {}
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "integer",
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
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "text",
    "logic": {}
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "text",
    "answer": "Howdy!"
}
```


### Multiple Choice
```
// Question
{
    "question_id": "<UUID>",
    "title": "Pick one",
    "hint": "",
    "required": false,
    "sequence_number": 0,
    "allow_multiple": false,    
    "type_constraint_name": "multiple_choice",
    "choices": [{
                     "question_choice_id": "<UUID>",
                     "choice": "bananas"
                },
                {
                     "question_choice_id": "<UUID>",
                     "choice": "apples"
                },
                {
                     "question_choice_id": "<UUID>",
                     "choice": "pears"
                }]
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "multiple_choice",
    "question_choice_id": "<UUID>",
    "choice": "bananas",
    "choice_number": 0
}
```


### Multiple Choice with Other
```
// Question
{
    "question_id": "<UUID>",
    "title": "Pick one or write in 'other'.",
    "hint": "",
    "required": false,
    "sequence_number": 0,
    "allow_multiple": false,    
    "type_constraint_name": "multiple_choice_with_other",
    "choices": [{
                     "question_choice_id": "<UUID>",
                     "choice": "bananas"
                },
                {
                     "question_choice_id": "<UUID>",
                     "choice": "apples"
                },
                {
                     "question_choice_id": "<UUID>",
                     "choice": "pears"
                }]
}

// Answer
Choice selected:
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "multiple_choice_with_other",
    "question_choice_id": "<UUID>",
    "choice": "bananas",
    "choice_number": 0
}

OR
other:
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "multiple_choice_with_other",
    "answer": "cherries"
}
```

