## Dokomo REST API

# Users

1. [Create API Token](#create-token)


### <a name="create-token"></a> Create API Token

```
GET /api/user/generate-api-token
```
An API Token can be used to access a user's account from a third-party application.

#### Parameters
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| duration | string | 2,592,000 (30 days) | The duration in seconds after which the token will expire. |

Example Response:
```json
{
    "token": "f9862a83d9974d3a92518c284cf72fcd",
    "expires_on": "2015-06-29T16:11:59.630092+00:00"
}
```

In order to make API requests using an API Token, include the following two headers in the request:

```
Token: <API Token>
Email: <Account Email Address>
```