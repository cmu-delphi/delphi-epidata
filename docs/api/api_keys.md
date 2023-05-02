---
title: API Keys
nav_order: 2
has_children: true
---

# Epidata API Keys

Anyone may access the Epidata API anonymously without providing any personal
data. If you choose to [register for an API key](https://forms.gle/hkBr5SfQgxguAfEt7), 
there are several ways to use your key to authenticate your requests:

## Via request parameter

The request parameter “api_key” can be used to pass the API key to the server.
Example:

    http://delphi.cmu.edu/epidata/covidcast/meta?api_key=your_api_key_here

## Via Basic Authentication

Another method is using the HTTP basic authorization header with the username
"epidata" and the API key as the password. Example:

```
curl -u 'epidata:your_api_key_here' https://delphi.cmu.edu/epidata/covidcast/meta
```

## Via Bearer Token

Another method is providing the key in a bearer token header. Example:

```
curl -H 'Authorization: Bearer your_api_key_here' https://delphi.cmu.edu/epidata/covidcast/meta
```
