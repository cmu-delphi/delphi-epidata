---
title: Epidata API Client Libraries
parent: Epidata API (Other Diseases)
nav_order: 1
---

# Epidata API Client Libraries.

Epidata clients are available for
[CoffeeScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.coffee),
[JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.js),
[Python](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.py),
and
[R](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19
Surveillance Streams from Facebook Survey CLI for county 06001 and days
`20200401` and `20200405-20200414` (11 days total).

For anyone looking for COVIDCast data, please visit our [COVIDCast Libraries](covidcast_clients.md).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.covidcast(callback, 'fb-survey', 'smoothed_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
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
  Epidata.covidcast(callback, 'fb-survey', 'smoothed_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001');
</script>
````

### Python


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
res = Epidata.covidcast('fb-survey', 'smoothed_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
````

### R


````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast('fb-survey', 'smoothed_cli', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
