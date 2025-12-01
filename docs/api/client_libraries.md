---
title: API Clients
nav_order: 6
---

# Getting Started with R and Python
{: .no_toc}

The [`epidatr`](https://cmu-delphi.github.io/epidatr/) (R) [`epidatpy`](https://cmu-delphi.github.io/epidatpy/) (Python) packages provide access to all the endpoints of the Delphi Epidata API, and can be used to make requests for specific signals on specific dates and in select geographic regions.

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Setup

### Installation

You can install these packages like this:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

You can install the stable version of `epidatr` from CRAN:

```r
install.packages("epidatr")
# Or use pak/renv
pak::pkg_install("epidatr")
```
If you want the development version, install from GitHub:

```r
remotes::install_github("cmu-delphi/epidatr", ref = "dev")
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

The `epidatpy` package will soon be [available on PyPI as `epidatpy`](https://pypi.org/project/epidatpy/).
Meanwhile, it can be [installed from GitHub](https://github.com/cmu-delphi/epidatpy/) with

```Python
pip install "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"
```

  </div>
</div>

### API Keys

The Delphi API requires a (free) API key for full functionality. While most endpoints are available without one, there are [limits on API usage for anonymous users](/api_keys.md), including a rate limit.

To generate your key, [register for a pseudo-anonymous account](https://api.delphi.cmu.edu/epidata/admin/registration_form).

  * **R:** See the `save_api_key()` function documentation for details on how to set up `epidatr` to use your API key.
  * **Python:** The `epidatpy` client will automatically look for this key in the environment variable `DELPHI_EPIDATA_KEY`. We recommend storing your key in a `.env` file, using `python-dotenv` to load it into your environment, and adding `.env` to your `.gitignore` file.

> **Note:** Private endpoints (i.e. those prefixed with `pvt_`) require a separate key that needs to be passed as an argument. These endpoints require specific data use agreements to access.
{: .note }

## Basic Usage

Fetching data from the Delphi Epidata API is simple. Suppose we are interested in the [`covidcast` endpoint](/covidcast.md), which provides access to a [wide range of data](/covidcast_signals.md) on COVID-19. Reviewing the endpoint documentation, we see that we [need to specify](/covidcast_api_queries.md) a data source name, a signal name, a geographic level, a time resolution, and the location and times of interest.

The `pub_covidcast()` function lets us access the `covidcast` endpoint:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
library(epidatr)
library(dplyr)

# Obtain the most up-to-date version of the smoothed covid-like illness (CLI)
# signal from the COVID-19 Trends and Impact survey for the US
epidata <- pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "nation",
  time_type = "day",
  geo_values = "us",
  time_values = epirange(20210105, 20210410)
)
head(epidata)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
from epidatpy import CovidcastEpidata, EpiDataContext, EpiRange

# Initialize client (caching enabled for 7 days)
epidata = EpiDataContext(use_cache=True, cache_max_age_days=7)

# Obtain the most up-to-date version of the confirmed cumulative cases
# from JHU CSSE for the US
apicall = epidata.pub_covidcast(
    data_source="jhu-csse",
    signals="confirmed_cumulative_num",
    geo_type="nation",
    time_type="day",
    geo_values="us",
    time_values=EpiRange(20210405, 20210410),
)
print(apicall.df().head())
```

  </div>
</div>

`pub_covidcast()` returns a `tibble` in R and an `EpiDataCall` (convertible to a pandas DataFrame via `.df()`) in Python. Each row represents one observation in the specified location on one day. The location abbreviation is given in the `geo_value` column, the date in the `time_value` column. Here `value` is the requested signal—in this case, the smoothed estimate of the percentage of people with COVID-like illness or case counts—and `stderr` is its standard error.

The Epidata API makes signals available at different geographic levels, depending on the endpoint. To request signals for all states instead of the entire US, we use the `geo_type` argument paired with `*` for the `geo_values` argument. (Only some endpoints allow for the use of `*` to access data at all locations. Check the help for a given endpoint to see if it supports `*`.)

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Obtain data for all states
pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "state",
  time_type = "day",
  geo_values = "*",
  time_values = epirange(20210105, 20210410)
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Obtain data for all states
epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    time_type="day",
    geo_values="*",
    time_values=EpiRange(20210405, 20210410),
).df()
```

  </div>
</div>

Alternatively, we can fetch the full time series for a subset of states by listing out the desired locations in the `geo_value` argument and using `*` in the `time_values` argument:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Obtain data for PA, CA, and FL
pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "state",
  time_type = "day",
  geo_values = c("pa", "ca", "fl"),
  time_values = "*"
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Obtain data for PA, CA, and FL
epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    time_type="day",
    geo_values="pa,ca,fl",
    time_values="*",
).df()
```

  </div>
</div>

## Getting versioned data

The Epidata API stores a historical record of all data, including corrections and updates, which is particularly useful for accurately backtesting forecasting models. To retrieve versioned data, we can use the `as_of` argument, which fetches the data as it was known on a specific date.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Obtain the signal as it was on 2021-06-01
pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "state",
  time_type = "day",
  geo_values = "pa",
  time_values = epirange(20210105, 20210410),
  as_of = "2021-06-01"
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Obtain the signal as it was on 2021-06-01
epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    time_type="day",
    geo_values="pa",
    time_values=EpiRange(20210405, 20210410),
    as_of="2021-06-01",
).df()
```

  </div>
</div>

We can also request all versions of the data issued within a specific time period using the `issues` argument.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# See how the estimate for a SINGLE day (March 1, 2021) evolved
# by fetching all issues reported between March and April 2021.
pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "state",
  time_type = "day",
  geo_values = "pa",
  time_values = "2021-03-01",
  issues = epirange("2021-03-01", "2021-04-30")
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# See how the estimate for a SINGLE day (March 1, 2021) evolved
# by fetching all issues reported between March and April 2021.
epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    time_type="day",
    geo_values="pa",
    time_values="2021-03-01",
    issues=EpiRange("2021-03-01", "2021-04-30"),
).df()
```

  </div>
</div>

Finally, we can use the `lag` argument to request only data that was reported a certain number of days after the event.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Fetch survey data for January 2021, but ONLY include data
# that was issued exactly 2 days after it was collected.
pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "state",
  time_type = "day",
  geo_values = "pa",
  time_values = epirange(20210101, 20210131),
  lag = 2
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Fetch survey data for January 2021, but ONLY include data
# that was issued exactly 2 days after it was collected.
epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    time_type="day",
    geo_values="pa",
    time_values=EpiRange(20210101, 20210131),
    lag=2,
).df()
```

  </div>
</div>

See `vignette("versioned-data")` for details and more ways to specify versioned data.

## Plotting

Because the output data is in a standard `tibble` (R) or `DataFrame` (Python) format, we can easily plot it using standard libraries like `ggplot2` or `matplotlib`.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
library(ggplot2)
ggplot(epidata, aes(x = time_value, y = value)) +
  geom_line() +
  labs(
    title = "Smoothed CLI from Facebook Survey",
    subtitle = "PA, 2021",
    x = "Date",
    y = "CLI"
  )
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
import matplotlib.pyplot as plt

# Fetch data for PA, CA, FL
apicall = epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    geo_values="pa,ca,fl",
    time_type="day",
    time_values=EpiRange(20210405, 20210410),
)

# Plot
fig, ax = plt.subplots(figsize=(6, 5))
(
    apicall.df()
    .pivot_table(values="value", index="time_value", columns="geo_value")
    .plot(xlabel="Date", ylabel="CLI", ax=ax, linewidth=1.5)
)
plt.title("Smoothed CLI from Facebook Survey")
plt.show()
```

  </div>
</div>

## Finding locations of interest

Most data is only available for the US. Select endpoints report other countries at the national and/or regional levels. Endpoint descriptions explicitly state when they cover non-US locations.

For endpoints that report US data, consult the geographic coding documentation for [COVID-19](/covidcast_geography.md) and for [other diseases](/geographic_codes.md) to see available geographic levels.

### International data

International data is available via

  * `pub_dengue_nowcast` (North and South America)
  * `pub_ecdc_ili` (Europe)
  * `pub_kcdc_ili` (Korea)
  * `pub_nidss_dengue` (Taiwan)
  * `pub_nidss_flu` (Taiwan)
  * `pub_paho_dengue` (North and South America)
  * `pvt_dengue_sensors` (North and South America)

## Finding data sources and signals of interest

Above we used data from [Delphi’s symptom surveys](https://delphi.cmu.edu/covid19/ctis/), but the Epidata API includes numerous data streams: medical claims data, cases and deaths, mobility, and many others. This can make it a challenge to find the data stream that you are most interested in.

The Epidata documentation lists all the data sources and signals available through the API for [COVID-19](/covidcast_signals.md) and for [other diseases](README.md#source-specific-parameters).

You can also use the client libraries to discover endpoints interactively:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Get a table of endpoint functions
avail_endpoints()
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# List sources available in the pub_covidcast endpoint
covidcast = CovidcastEpidata(use_cache=True)
print(covidcast.source_names())

# List signals available for a specific source (e.g., jhu-csse)
print(covidcast.signal_names("jhu-csse"))
```

  </div>
</div>

## Legacy Clients

Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/), [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R), and [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.js),
but its use is discouraged.

The following samples show how to import the library and fetch Delphi’s COVID-19 Surveillance Streams from Facebook Survey CLI for county `06001` and days `20200401` and `20200405-20200414` (11 days total).

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
    <button data-tab="js">JavaScript</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

Install [`delphi-epidata` from PyPI](https://pypi.org/project/delphi-epidata/) with
`pip install delphi-epidata`.

```python
from delphi_epidata import Epidata
# Configure API key, if needed.
#Epidata.auth = ('epidata', <your API key>)
res = Epidata.covidcast('fb-survey', 'smoothed_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">


```R
# Configure API key, if needed.
#option('epidata.auth', <your API key>)
source('delphi_epidata.R')
res <- Epidata$covidcast('fb-survey', 'smoothed_cli', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">

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
  </div>

</div>

