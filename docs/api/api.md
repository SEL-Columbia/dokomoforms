## Dokomo REST API

Dokomo forms provides a RESTful API through which applications can interact with the system. The Dokomo application itself makes extensive use of the API in order to submit completed surveys and otherwise interact with clients.

**At present, JSON is the only supported media type.**

### Authentication

Authentication is done through normal login + session cookies. Later we may add in HTTP Basic Auth to support other clients. API requests can also be performed with a valid API Token.

### Requests, Responses, and Errors

The API will support the **GET**, **POST**, **PUT**, and **DELETE** HTTP methods.

For IE < 9 compatibility purposes, **PUT** and **DELETE** requests can also be emulated by POSTing with the `_method=[put|delete]`.

Some GET requests have optional parameters which will affect the results returned in the response.

POST requests should include a valid JSON object as the body payload.

On error, the server will respond with the corresponding HTTP response code, and the resulting JSON in the body will contain an `error` property with a message describing the error.

### [Surveys](surveys.md)
### [Submissions](submissions.md)
### [Users](users.md)