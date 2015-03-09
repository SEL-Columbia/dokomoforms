<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Client to Server Interaction](#client-to-server-interaction)
  - [Survey schema](#survey-schema)
  - [Survey response](#survey-response)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Client to Server Interaction

This occurs via message passing in json

## Survey schema
```
{
    "survey_id": "1a2a3a4a",
    "questions": [
        {
            "id": "UUID",
            "label": "Health facility name",
            "type": "text"
        },
        {
            "id": "UUID",
            "label": "Enter a number",
            "type": "number",
            "min": 5,
            "max": 10,
            "default": 1
        },
        {   
            "id": "UUID",
            "label": "Location"
            "type": "gps",
        },
        {
            "id": "UUID",
            "type": "text",
            "label": "What are your favorite pies?"
        },
        {   
            "id": "UUID",
            "type": "choice",
            "label": "Pick one",
            "choices": [                   
                ["choice1", "Banana"],    // should labels and ids be the same?
                ["choice2", "Apple"],
                ["choice3", "Pear"]
            ]
        },
        {
            "id": "UUID",
            "type": "image",
            "label": "Your profile picture"
        }
    ]
}
```

## Survey response
```
{
    survey_id: '1a2a3a4a',
    answer_id: 'UUID', // randomly generated. might be used more than once (for updates)
    answers: [{
        question_id: 'UUID',
        answer: 'string value'
    }, ...]
}
```
