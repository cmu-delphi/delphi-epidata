---
title: Epidata API Client Libraries
parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 1
---

# Epidata API Client Libraries

For anyone looking for COVIDCast data, please visit our [COVIDCast Libraries](covidcast_clients.md).

A full-featured Epidata client for R is available at
[epidatr](https://github.com/cmu-delphi/epidatr) and
[also on CRAN](https://cran.r-project.org/web/packages/epidatr/index.html).

We are currently working on a new full-featured Epidata client for Python. It is not ready
for release yet, but you can track our development progress and help us test it out at
[epidatpy](https://github.com/cmu-delphi/epidatpy).

In the meantime, minimalist Epidata clients remain available for
[Python](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.py),
[JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.js),
and
[R (legacy)](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19
Surveillance Streams from Facebook Survey CLI for county 06001, and days
`20200401` and `20200405-20200414` (11 days total).

### R

````R
# [Optional] configure your API key, if desired
# Interactive. See https://cmu-delphi.github.io/epidatr/articles/epidatr.html#api-keys for details.
#save_api_key()
# Import
library(epidatr)
# Fetch data
res <- pub_covidcast('fb-survey', 'smoothed_cli', 'county', 'day', geo_values = '06001',
                     time_values = c(20200401, 20200405:20200414))
cat(res)
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
# [Optional] configure your API key, if desired
#Epidata.auth = ('epidata', <your API key>)
# Fetch data
res = Epidata.covidcast('fb-survey', 'smoothed_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
````

### JavaScript (in a web browser)

The minimalist JavaScript client does not currently support API keys. If you need API key support in JavaScript, contact delphi-support+privacy@andrew.cmu.edu.

````html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.covidcast('fb-survey', 'smoothed_cli', 'day', 'county', [20200401, EpidataAsync.range(20200405, 20200414)], '06001').then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
````

### R (legacy)

```R
# [Optional] configure your API key, if desired
#option('epidata.auth', <your API key>)
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast('fb-survey', 'smoothed_cli', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
```
