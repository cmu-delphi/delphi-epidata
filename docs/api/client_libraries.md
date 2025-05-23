---
title: API Clients
parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 1
---

# Epidata API Clients

To access Delphi Epidata programmatically, we recommend our client libraries:

- R: [epidatr](https://cmu-delphi.github.io/epidatr/),
- Python: [epidatpy](https://cmu-delphi.github.io/epidatpy/) (recommended) and [delphi-epidata](https://pypi.org/project/delphi-epidata/),
- Javascript: [delphi-epidata](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.js).

For anyone looking for COVIDCast data, please visit our [COVIDCast API Client Libraries](covidcast_clients.md).

The following samples show how to import the library and fetch Delphi's
COVID-19 Surveillance Streams from Facebook Survey CLI for county 06001 and days
`20200401` and `20200405-20200414` (11 days total).

### R

Install [`epidatr` from CRAN](https://cran.r-project.org/package=epidatr)
with `install.packages("epidatr")`.

```r
# Configure API key interactively, if needed. See
# https://cmu-delphi.github.io/epidatr/articles/epidatr.html#api-keys for details.
#save_api_key()
library(epidatr)
data <- pub_covidcast('fb-survey', 'smoothed_cli', 'county', 'day', geo_values = '06001',
                     time_values = c(20200401, 20200405:20200414))
cat(data)
```

### Python

The `epidatpy` package will soon be [available on PyPI as `epidatpy`](https://pypi.org/project/epidatpy/).
Meanwhile, it can be [installed from GitHub](https://github.com/cmu-delphi/epidatpy/) with
`pip install "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"`.

```python
# Configure API key, if needed.
# https://github.com/cmu-delphi/epidatpy/blob/dev/docs/index.rst#api-keys

from epidatpy import EpiDataContext, EpiRange

# Create the client object.
epidata = EpiDataContext()
apicall = epidata.pub_covidcast(
    data_source="jhu-csse",
    signals="confirmed_cumulative_num",
    geo_type="nation",
    time_type="day",
    geo_values="us",
    time_values=EpiRange(20210405, 20210410),
)
print(apicall.df())
```

Install [`delphi-epidata` from PyPI](https://pypi.org/project/delphi-epidata/) with
`pip install delphi-epidata`.

```python
from delphi_epidata import Epidata
# Configure API key, if needed.
#Epidata.auth = ('epidata', <your API key>)
res = Epidata.covidcast('fb-survey', 'smoothed_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
```

### JavaScript (in a web browser)

The minimalist JavaScript client does not currently support API keys.
If you need API key support in JavaScript, contact delphi-support+privacy@andrew.cmu.edu.

```html
<script src="delphi_epidata.js"></script>
<script>
  EpidataAsync.covidcast(
    "fb-survey",
    "smoothed_cli",
    "day",
    "county",
    [20200401, EpidataAsync.range(20200405, 20200414)],
    "06001"
  ).then((res) => {
    console.log(
      res.result,
      res.message,
      res.epidata != null ? res.epidata.length : 0
    );
  });
</script>
```

### R (legacy)

The old Delphi Epidata R client is available
[here](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R),
but its use is discouraged.

```R
# Configure API key, if needed.
#option('epidata.auth', <your API key>)
source('delphi_epidata.R')
res <- Epidata$covidcast('fb-survey', 'smoothed_cli', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
```
