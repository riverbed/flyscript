This document describes version 1.0 of the Riverbed Common REST API as implemented by Cascade Shark systems.

The Common REST API is used to obtain general system information and for authentication. 

It is assumed that the reader has practical knowledge of RESTful APIs, so the documentation does not go into detail about what REST is and how to use it. Instead the documentation focuses on what data can be accessed or modified, how to access it, and how to encode requests and responses.

The Resources section lists the supported REST resources and the methods supported on these resources. For each operation, the document describes what the operation does, the specific HTTP method and URL used, the data types used for requests and responses (if any) and any required or optional URL parameters.

The Errors section lists the various error codes that may be returned from REST API operations.

### Data Encoding

Most resources exposed by the API support both XML and JSON encoding for requests and responses. The selection of the specific encoding is accomplished through the use of HTTP headers.

The <code>Accept</code> header should be included with all API requests, and it is used to control the encoding of the response body. To specify XML encoding, the header should be set to <code>Accept: text/xml</code>, and to specify JSON encoding, the header should be set to <code>Accept: application/json</code>. If the <code>Accept</code> header is omitted, the default encoding is XML.

The <code>Content-Type</code> header must be included with all PUT or POST requests that include a request body. To specify XML encoding, the header should be set to <code>Content-Type: text/xml</code>. To specify JSON encoding, the header should be set to <code>Content-Type: application/json</code>.

Some resources support alternative content types for requests and responses, as identified in the specific resource documentation below. 

### Authorization

This common API and other service-specific APIs support various methods of user authentication and authorization.

* **BASIC** (*HTTP Basic Authentication*): The username and password are passed using the <code>Authorization</code> HTTP header in each request.

* **COOKIE** (*Cookie-based Session Authentication*): A valid username and password combination are transmitted in an explicit login request which returns a session identifier. Subsequent requests include this session identifier as a HTTP cookie.

* **OAUTH_2_0** (*OAuth version 2.0 Authentication*) (TBD)