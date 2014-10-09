# About

Dokomo [どこも](http://tangorin.com/general/%E3%81%A9%E3%81%93%E3%82%82) Forms is a mobile data collection technology that doesn't suck.
 


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
    response_id: 'UUID', // randomly generated. might be used more than once (for updates)
    responses: [{
        question_id: 'UUID',
        value: 'string value'
    }, ...]
}
```
