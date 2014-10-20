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
        "id": "<UUID>",
        "name": "Batcave inventory",
        "questions": [{
            "id": "<UUID>"
            "label": "Batmobile jet fuel reserves (L)",
            "type": "integer"
        }]
    }
]
```

### Get Survey
`GET /surveys/<UUID>`

Response:
```
{
    "id": "<UUID>",
    "name": "Batcave inventory",
    "questions": [{
        "id": "<UUID>"
        "label": "Batmobile jet fuel reserves (L)",
        "type": "integer"
    }]
}
```


### Create Survey
`POST /surveys`

Request data:
```
{
    "name": "Batcave inventory",
    "questions": [{
        "id": "<UUID>"
        "label": "Batmobile jet fuel reserves (L)",
        "type": "integer"
    }]
}
```

### Update Survey
`POST /surveys/<UUID>`

Request data:
```
{
    "id": "<UUID>",
    "name": "Batcave inventory v2",
    "questions": [
        {
            "id": "<UUID>"
            "label": "Update this question (has an id)",
            "type": "integer"
        },
        {
            "label": "Add a new question (no id)",
            "type": "text"
        }
    ]
}
```

### Delete Survey
`DELETE /surveys/<UUID>`
or 
`POST /surveys/<UUID>` with argument `_method=DELETE`


## Survey Responses

### Submit Survey
`POST /surveys/<UUID>/responses`





### Question & Answer Objects

#### Location
```
// Question
{
    "id": "<UUID>",
    "label": "Location",
    "type": "location"
}

// Answer
{
    "id": "<UUID>",
    "answer": [<longitude>, <latitude>]
}
```


#### Integer
```
// Question
{
    "id": "<UUID>",
    "label": "Number from 5 to 10",
    "type": "integer",
    "min": 5,
    "max": 10,
    "default": 1,
    "name": "num"
}

// Answer
{
    "id": "<UUID>",
    "answer": 6
}
```

#### Text
```
// Question
{
    "id": "<UUID>",
    "label": "Description"
    "type": "text"
}

// Answer
{
    "id": "<UUID>",
    "answer": "Howdy!"
}
```


#### Multiple Choice
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


