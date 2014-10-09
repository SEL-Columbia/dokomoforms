# About

Dokomo [どこも](http://tangorin.com/general/%E3%81%A9%E3%81%93%E3%82%82) Forms is a mobile data collection technology that doesn't suck.
 


## Survey schema
```
{
    survey_id: '1a2a3a4a',
    questions: [{
        id: 'UUID',
        name: 'Health facility name',
        type: 'text'
    }]
}
```

## Survey response
```
{
    survey_id: '1a2a3a4a',
    response_id: 'UUID', // randomly generated. might be used more than once (for updates)
    responses: { // multiple types
        'UUID': 'string value',
        'UUID2': 12345,
        'UUID4': [40.809400, -73.960029], // coordinates
        'UUID3': ['multiple', 'values'] // would we need this?
    }
}
```
