---
title: API Keys
nav_order: 1
has_children: true
---

# Epidata API Keys

Anyone may access the Epidata API anonymously without providing any personal
data. Anonymous API access is subject to the following restrictions; they may
change as we learn more about their impact:

1. public datasets only
1. rate-limited to 60 requests per hour
1. only two parameters may have multiple selections

For example, a query for three signals on one date across all counties can be
submitted anonymously, but a query for three signals on a period of four weeks
across all counties requires an API key.

An API key is a pseudonymous access token that grants privileged access to the
Epidata API. You can request an API key by
[registering with us](https://api.delphi.cmu.edu/epidata/admin/registration_form).
Privileges of registration may include:

1. no rate limit
1. no limit on multiple selections

We require an email address for all registrations so that we can contact you to
resolve problems with excessive or abnormal usage patterns. Any additional
personal information you provide to us at registration will be much appreciated,
because it will help us understand what our data is used for and inform our
plans and priorities, but is voluntary. For more information on how we use and
store the information you provide us at registration time, see our
[privacy statement](privacy_statement.md).

## Usage

If you choose to
[register for an API key](https://api.delphi.cmu.edu/epidata/admin/registration_form),
there are several ways to use your key to authenticate your requests:

### Using a client

* covidcast
  * [R client](https://cmu-delphi.github.io/covidcast/covidcastR/reference/covidcast_signal.html#api-keys-1)
  * [Python client](https://cmu-delphi.github.io/covidcast/covidcast-py/html/signals.html#covidcast.use_api_key)
* [epidatr](https://github.com/cmu-delphi/epidatr#api-keys)
* [delphi-epidata](https://cmu-delphi.github.io/delphi-epidata/api/client_libraries.html)

### Via request parameter

The request parameter “api_key” can be used to pass the API key to the server.
Example:

    https://api.delphi.cmu.edu/epidata/covidcast/meta?api_key=your_api_key_here

### Via Basic Authentication

Another method is using the HTTP basic authorization header with the username
"epidata" and the API key as the password. Example:

```
curl -u 'epidata:your_api_key_here' https://api.delphi.cmu.edu/epidata/covidcast/meta
```

### Via Bearer Token

Another method is providing the key in a bearer token header. Example:

```
curl -H 'Authorization: Bearer your_api_key_here' https://api.delphi.cmu.edu/epidata/covidcast/meta
```
