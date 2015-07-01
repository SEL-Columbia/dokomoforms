# Nodes

1. [List Nodes](#list-nodes)
2. [Get a Single Node](#single-node)
3. [Create a New Node](#create-node)
4. [Delete a Node](#delete-node)

Nodes are standalone objects which represent a single question. A Node can be one of two types, AnswerableNode and NonAnswerableNode. All Nodes are answerable with the exception of the 'note' type. The type is defined by the Node's `type_constraint` property.

When a Node gets associated with a Survey, it gets wrapped in a SurveyNode. The SurveyNode can be thought of as a specific instance of a Node -- it is the linking object between the Node (i.e. question) and the Survey. This allows multiple Surveys to include a certain question while maintaining the ability to identify the question by a unique identifier, which simplifies the aggregation of answers to questions and makes the data easy to work with.

### <a name="list-nodes"></a> List Nodes

```
GET /api/v0/nodes
```
#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| offset | integer | 0 | The offset of the result set. |
| limit | integer | 100 | Limits the number of results in the result set. |
| order_by | string | created_on:DESC | A comma-delimited list of Node properties with order direction, e.g. title:ASC,type:DESC |
| type | string |  | Filters on the `type_constraint` property of the Node. |
| draw | integer |  | If included in the request, the `draw` parameter will be returned in the response unaltered. |

*Note: All parameters are optional.*

If there is an error, the response will contain a single `error` property containing the error message.

#### Example Response:
```json
{
    "limit": 4,
    "offset": 5,
    "nodes": [
        {
            "id": "8e6e6905-3d18-4230-87ce-435fd074d421",
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "When did this occur?"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "timestamp",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00"
        },
        {
            "id": "ef8edd1f-4850-41f2-9471-86189239ec64",
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "Exterior Photograph"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "photo",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00"
        },
        {
            "id": "f6a2536a-3f92-4e38-84e7-f22fcba49dba",
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "Location"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "location",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00"
        },
        {
            "id": "f81085ad-9e60-4128-ac53-aa3ac2f88fa7",
            "deleted": false,
            "languages": [
                "English"
            ],
            "title": {
                "English": "Patient Birthdate"
            },
            "hint": {
                "English": ""
            },
            "allow_multiple": false,
            "allow_other": false,
            "type_constraint": "date",
            "logic": {},
            "last_update_time": "2015-07-01T18:17:18.984452+00:00"
        }
    ]
}
```

### <a name="single-node"></a> Get a Single Node

```
/api/v0/nodes/<Node_UUID>
```

#### Example Response:
```json
{
    "id": "8e6e6905-3d18-4230-87ce-435fd074d421",
    "deleted": false,
    "languages": [
        "English"
    ],
    "title": {
        "English": "When did this occur?"
    },
    "hint": {
        "English": ""
    },
    "allow_multiple": false,
    "allow_other": false,
    "type_constraint": "timestamp",
    "logic": {},
    "last_update_time": "2015-07-01T18:17:18.984452+00:00"
}
```

### <a name="create-node"></a> Create a New Node

```
POST /api/v0/nodes
```
A Node (again, think 'question') can be one of several types, defined by its `type_constraint` value, which enforces the types of acceptable answer values:

```
NODE_TYPES = {
    'text': TextQuestion,
    'photo': PhotoQuestion,
    'integer': IntegerQuestion,
    'decimal': DecimalQuestion,
    'date': DateQuestion,
    'time': TimeQuestion,
    'timestamp': TimestampQuestion,
    'location': LocationQuestion,
    'facility': FacilityQuestion,
    'multiple_choice': MultipleChoiceQuestion,
    'note': Note,
}
```

The `allow_multiple` property defines whether this Node (question) should accept multiple answers. Defaults to `false`.

The `allow_other` property defines whether this Node (question) should allow an 'other' answer option. Defaults to `false`.

#### Example Request Body:
```json
{
    "title": {
        "English": "text_node"
    },
    "hint": {
        "English": "Some test hint."
    },
    "type_constraint": "text",
    "logic": {},
}
```

#### Example Response:
```json
{
    "id": "d1091c27-ae98-4272-957f-f28c236fc832",
    "deleted": false,
    "languages": [
        "English"
    ],
    "title": {
        "English": "text_node"
    },
    "hint": {
        "English": "Some test hint."
    },
    "allow_multiple": false,
    "allow_other": false,
    "type_constraint": "text",
    "logic": {},
    "last_update_time": "2015-07-01T20:22:37.461764+00:00"
}
```

Multiple Choice nodes have a `choices` property:

#### Example Request Body (`multiple_choice` type)
```json
{
    "title": {"English": "Which food is the tastiest?"},
    "hint": {
        "English": "Some test hint."
    },
    "allow_other": true,
    "type_constraint": "multiple_choice",
    "logic": {},
    "choices": [
        {
            "choice_text": {
                "English": "Bagel"
            }
        },
        {
            "choice_text": {
                "English": "Burger"
            }
        }
    ]
}
```

#### Example Response:
```json
{
    "id": "233616eb-d923-4b83-87af-620f011c4d34",
    "deleted": false,
    "title": {
        "English": "Which food is the tastiest?"
    },
    "hint": {
        "English": "Some test hint."
    },
    "choices": [
        {
            "choice_id": "d06ac0fb-0281-4ed4-8729-e79c08d6c8aa",
            "choice_text": {
                "English": "Bagel"
            }
        },
        {
            "choice_id": "7b66b5da-0fce-4dfd-8a65-d9fd67b69130",
            "choice_text": {
                "English": "Burger"
            }
        }
    ],
    "allow_multiple": false,
    "allow_other": true,
    "type_constraint": "multiple_choice",
    "logic": {},
    "last_update_time": "2015-07-01T20:38:43.660554+00:00"
}
```

### <a name="delete-node"></a> Delete Node

```
DELETE /api/v0/nodes/<Node_UUID>
```

Delete requests have no response payload. A successful deletion will respond with an empty `204` No Content status code.

**Note**: Deletions are non-destructive; data is simply marked as deleted, and will no longer appear in standard queries.
