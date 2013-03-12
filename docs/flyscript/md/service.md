rvbd.common.service
===========

{module rvbd.common.service}

Service
-----

{class Service}

{method authenticate}
{method logout}
{method ping}
{method check_api_versions}

Authentication
----

{class Auth silent}

Most REST resource calls require authentication.  Devices will support one
or more authentication methods.  The following methods may be supported:

- `Auth.OAUTH` - OAuth 2.0 based authentication using an access code.  The
     access code is used to retrieve an access token which is used 
     in subsequent REST calls.

- `Auth.COOKIE` - session based authentication via HTTP Cookies.  The initial
     authentication uses username and password.  On success, an HTTP
     Cookie is set and used for subsequesnt REST calls.

- `Auth.BASIC` - simple username/password based HTTP Basic authentication.  

When a Service object is created, the user may either pass an authentication
object to the constructor, or later passed to the `service.authenticate()`
method. 

### UserAuth

{class UserAuth}

### OAuth

{class OAuth}
