Dokomoform's REST JSON API.

## Generating an API token

POST a JSON message to the `/generate-api-token` endpoint in this format:

```
{
    "email": "<e-mail address>",
    "duration": <duration in seconds>
}
```

The `duration` field is optional. Durations longer than 365 days are not allowed.

Response:
```
{
    "token": "<API token>",
    "expires_on: "<expiration time>"
}
```

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
            "sequence_number": 0,
            "allow_multiple": false,
            "type_constraint_name": "integer",
            "logic": {
                "required": false,
                "with_other": false
            },
            "choices": [],
            "branches": []
        }]
    }
]
```

The minimal amount of `logic` is always `required` and `with_other`.

If `type_constraint_name` is `multiple_choice` there will be a `choices` field like this:

```
"choices": [{
             "question_choice_id": "<UUID>",
             "choice": "bananas",
             "choice_number": "0"
            }]
```

If `type_constraint_name` is `multiple_choice` there can be a `branches` field like this:

```
"branches": [{
             "question_choice_id": "<UUID>",
             "to_question_id": "<UUID>"
            }]
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
        "sequence_number": 0,
        "allow_multiple": false,
        "type_constraint_name": "integer",
        "logic": {
            "required": false,
            "with_other": false
        },
        "choices": [],
        "branches": []
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
        "allow_multiple": null,
        "logic": {
            "required": false,
            "with_other": false
        },
        "choices": [],
        "branches": []
    }]
}
```

If you try to add a survey with a title that already exists for that user, a number surrounded by parentheses will be appended to the title. 

If `type_constraint_name` is `multiple_choice`, the question dict should also contain

```
"choices": ["choice 0", "choice 1", "choice 2"]
```

If you are creating a multiple choice question with branching, the question dict should also contain (everything is 0-indexed)

```
"branches": [{
              "choice_number": "0",
              "to_question_number": "1"
             }]
```

If you want to make a question required, add `{"required": true}` in the `logic` field.

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
        "allow_multiple": false,
        "logic": {
            "required": false,
            "with_other": false
        },
        "choices": [],
        "branches": []
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
            "question_id": "<UUID>",
            "title": "Update this question (has an id)",
            "type_constraint_name": "text",
            "sequence_number": null,
            "hint": null,
            "allow_multiple": null,
            "logic": {
                "required": false,
                "with_other": false
            },
            "choices": [],
            "branches": []
        },
        {
            "title": "Add a new question (no id)",
            "type_constraint_name": "text",
            "sequence_number": null,
            "hint": null,
            "allow_multiple": null,
            "logic": {
                "required": false,
                "with_other": false
            },
            "choices": [],
            "branches": []
        }
    ]
}
```

Updates are non-destructive. Rather than updating in-place, a new survey will be created with the given title and existing submissions will be copied over. The existing survey will be renamed like so:

`My fancy title` &rarr; `My fancy title (new version created on 2014-11-06T13:19:47.875324)`

The request for `update` is very similar to the one for `create`. The main difference is that if you want to update a question rather than create a new one, you need to supply the `question_id`. All other fields must be supplied as well.

For `questions`, `choices`, and `branches`, any element "left out" (not present in the `update` request) will be deleted.

Submission data will survive for choices that remain after the update (unchanged text).

All sequence numbers will be reassigned after the update (so you can rearrange questions -- take care to update the branches as well).



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
            "allow_multiple": false,
            "logic": {
                "required": false,
                "with_other": false
            },
            "choices": [],
            "branches": []
        },
        {
            "question_id": "<UUID>",
            "title": "Add a new question (no id)",
            "type_constraint_name": "text",
            "sequence_number": 1,
            "hint": "",
            "allow_multiple": false,
            "logic": {
                "required": false,
                "with_other": false
            },
            "choices": [],
            "branches": []
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

A note for any submission: if a question has `allow_multiple` set to `True`, you can answer it more than once by including several `answer` entries in the submission JSON. This is also how the answers will be displayed.

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
            "answer": 6,
            "choice": null,
            "choice_number: null,
            "is_other": false
        }]
    }
]
```

If `type_constraint_name` is `multiple_choice`, and a choice is selected, an entry in the `answers` list will look like this:

```
"answer_id": "<UUID>",
"question_id": "<UUID>",
"type_constraint_name": "multiple_choice",
"answer": "<UUID>",
"choice": "bananas",
"choice_number": 0,
"is_other": false
```

If `type_constraint_name` is `multiple_choices`, `with_other` in `logic` is `true`, and an "other" value was submitted instead of a choice, `is_other` will be `true`.

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
        "answer": 6,
        "choice": null,
        "choice_number: null,
        "is_other": false
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
        "answer": 6,
        "is_other: false
    }]
}
```

If the question to be answered is a `multiple_choice` question and `with_other` is true, and if an "other" value is supplied, `is_other` should be true.

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
        "answer": 6,
        "choice": null,
        "choice_number: null,
        "is_other": false
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
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "location",
    "logic": {
        "required": false,
        "with_other": false
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "location",
    "answer": [<longitude>, <latitude>],
    "choice": null,
    "choice_number: null,
    "is_other": false
}
```


### Date
```
// Question
{
    "question_id": "<UUID>",
    "title": "Date",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "date",
    "logic": {
        "required": false,
        "with_other": false
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "date",
    "answer": "1970-01-15",
    "choice": null,
    "choice_number: null,
    "is_other": false
}
```

The date should be given as `"YYYY-MM-DD"` - year, month, date


### Time (with timezone)
```
// Question
{
    "question_id": "<UUID>",
    "title": "Time",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "time",
    "logic": {
        "required": false,
        "with_other": false
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "time",
    "answer": "12:59:00-04:00",
    "choice": null,
    "choice_number: null,
    "is_other": false
}
```

The time should be given as `"HH:MM:SS{+,-}UTC"` - hour, minute, second, UTC offset. See http://en.wikipedia.org/wiki/ISO_8601

If seconds are not provided (`HH:MM{+,-}UTC`, `12:59-04:00`), the default is 0. The response answer will look like `HH:MM:00{+,-}UTC`

If the UTC offset is not provided, I believe the default is the time zone of the database... which is probably not what you want. At all.


### Integer
```
// Question
{
    "question_id": "<UUID>",
    "title": "Number from 5 to 10",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "integer",
    "logic": {
        "required": false,
        "with_other": false
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "integer",
    "answer": 6,
    "choice": null,
    "choice_number: null,
    "is_other": false
}
```


### Text
```
// Question
{
    "question_id": "<UUID>",
    "title": "Description",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,
    "type_constraint_name": "text",
    "logic": {
        "required": false,
        "with_other": false
    },
    "choices": [],
    "branches": []
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "text",
    "answer": "Howdy!",
    "choice": null,
    "choice_number: null,
    "is_other": false
}
```


### Multiple Choice
```
// Question
{
    "question_id": "<UUID>",
    "title": "Pick one",
    "hint": "",
    "sequence_number": 0,
    "allow_multiple": false,    
    "type_constraint_name": "multiple_choice",
    "logic": {
        "required": false,
        "with_other": false
    },
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
    "sequence_number": 0,
    "allow_multiple": false,    
    "type_constraint_name": "multiple_choice",
    "logic": {"with_other": true}
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
                }],
    "branches": []
}

// Answer
{
    "answer_id": "<UUID>",
    "question_id": "<UUID>",
    "type_constraint_name": "multiple_choice",
    "answer": "<UUID>",
    "choice": "bananas",
    "choice_number": 0,
    "is_other": false
}
```

If `with_other` is true, an answer can either be a `question_choice_id` (if `is_other` is false) or an "other" value (if `is_other` is true). 
