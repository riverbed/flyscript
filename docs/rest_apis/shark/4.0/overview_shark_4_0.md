This document describes the RESTful APIs exported by Cascade Shark products.

It is assumed that the reader has practical knowledge of RESTful APIs, so the documentation does not go into detail about what REST is and how to use it. Instead the documentation focuses on what data can be accessed or modified, how to access it, and how to encode requests and responses.

The remainder of this section lists the high level functionality exposed by the REST API and describes the data encodings for objects that are used to encode information for requests and responses.

The Resources section lists the supported REST resources and the methods supported on these resources. For each operation, the document describes what the operation does, the specific HTTP method and URL used, the data types used for requests and responses (if any) and any required or optional URL parameters.

The Data Types section describes commonly used data types in the REST API, including example encodings in both JSON and XML.

The Errors section lists the various error codes that may be returned from REST API operations.

### Functionality

The Shark REST API provides programmable access to virtually all of the functionality implemented by the shark appliance, including:

- Applying views and obtaining view output

- Enumerating and examining packet data sources on the appliance (interfaces, capture jobs, trace clips, and files)

- Creating trace clips, uploading

- Extracting packet data from the appliance

- Extracting and modifiying system configuration, including user configuration, capture job management, basic system configuration, etc.

- Access system version information and apply system updates

**NOTE**: Resources and methods used for authentication to the shark appliance through the API, and other resources related to querying for system information are implemented by the [Riverbed Common REST API](common_1_0_doc.html). Before accessing the Shark API, please familiarize yourself with the Common API documentation.

### Data Encoding

Most resources exposed by the API support both XML and JSON encoding for requests and responses. The selection of the specific encoding is accomplished through the use of HTTP headers.

The <code>Accept</code> header should be included with all API requests, and it is used to control the encoding of the response body. To specify XML encoding, the header should be set to <code>Accept: text/xml</code>, and to specify JSON encoding, the header should be set to <code>Accept: application/json</code>. If the <code>Accept</code> header is omitted, the default encoding is XML.

The <code>Content-Type</code> header must be included with all PUT or POST requests that include a request body. To specify XML encoding, the header should be set to <code>Content-Type: text/xml</code>. To specify JSON encoding, the header should be set to <code>Content-Type: application/json</code>.

Some resources support alternative content types for requests and responses, as identified in the specific resource documentation below. 



