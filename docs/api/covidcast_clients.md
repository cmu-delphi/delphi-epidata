---
title: API Clients
parent: COVIDcast Epidata API
nav_order: 1
---

# COVIDcast API Clients

Dedicated COVIDcast clients are available for several languages:

* R: [covidcast](https://cmu-delphi.github.io/covidcast/covidcastR/)
* Python: [covidcast](https://cmu-delphi.github.io/covidcast/covidcast-py/html/)

These packages provide a convenient way to obtain COVIDcast data as a data frame
ready to be used in further analyses, and provide convenient mapping and
analysis functions. For installation instructions and examples, consult their
respective webpages.

## Generic Epidata Clients

More generic clients that support the entire Epidata API are available as well.
Epidata clients are available for
[CoffeeScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.coffee),
[JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.js),
[Python](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.py),
and
[R](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19
Surveillance Streams from Facebook Survey CLI for county 06001 and days
`20200401` and `20200405-20200414` (11 days total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.covidcast(callback, 'fb-survey', 'raw_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
````

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="jquery.js"></script>
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  var callback = function(result, message, epidata) {
    console.log(result, message, epidata != null ? epidata.length : void 0);
  };
  Epidata.covidcast(callback, 'fb-survey', 'raw_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001');
</script>
````

### Python

**Note:** For COVIDcast usage, Python users should prefer the [covidcast-py
package](https://cmu-delphi.github.io/covidcast/covidcast-py/html/); these
instructions are for advanced users who want access to the entire Epidata API,
including data on influenza, dengue, and norovirus.

Optionally install the [package from PyPI](https://pypi.org/project/delphi-epidata/) using pip(env):
````bash
pip install delphi-epidata
````

Otherwise, place
[`delphi_epidata.py`](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.py)
in the same directory as your Python script.

````python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.covidcast('fb-survey', 'raw_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
````

### R

**Note:** For COVIDcast usage, R users should prefer the [covidcast
package](https://cmu-delphi.github.io/covidcast/covidcastR/); these instructions
are for advanced users who want access to the entire Epidata API, including data
on influenza, dengue, and norovirus.

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast('fb-survey', 'raw_cli', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
