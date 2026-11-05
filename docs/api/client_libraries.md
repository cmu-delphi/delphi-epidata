---
title: API Clients
nav_order: 6
---

# Getting Started with R and Python
{: .no_toc}

The [`epidatr`](https://cmu-delphi.github.io/epidatr/) (R) and [`epidatpy`](https://cmu-delphi.github.io/epidatpy/) (Python) packages provide access to all the endpoints of the Delphi Epidata API, and can be used to make requests for specific signals on specific dates and in select geographic regions. Modern Delphi API clients natively support the Delphi V5 API. To explore endpoints, filter syntax, rate limits, and runnable recipes interactively, see the [Epidata API Guide](https://delphi.cmu.edu/epidata/v5/guide#start).

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Setup

### Installation

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

You can install the stable version of `epidatr` from CRAN:

```r
install.packages("epidatr")
# Or use pak
pak::pkg_install("epidatr")
```
If you want the development version, install from GitHub:

```r
pak::pkg_install("cmu-delphi/epidatr@dev")
# Or using remotes
remotes::install_github("cmu-delphi/epidatr", ref = "dev")
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

Install `epidatpy` from PyPI:

```sh
pip install epidatpy
```

Or install the latest development version from GitHub:

```sh
pip install "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"
```

  </div>
</div>

### API Keys

The Delphi API requires a (free) API key for full functionality. While most endpoints are available without one, there are [limits on API usage for anonymous users](api_keys.md), including rate limits.

To generate your key, [register for a free account](https://api.delphi.cmu.edu/epidata/admin/registration_form).

  * **R:** `epidatr` automatically looks for this key in the environment variable `DELPHI_EPIDATA_KEY` (e.g. in your `~/.Renviron` file). You can also configure it using the `save_api_key()` function.
  * **Python:** `epidatpy` automatically looks for this key in the environment variable `DELPHI_EPIDATA_KEY`. We recommend storing your key in a `.env` file and loading it with `python-dotenv`.

> **Note:** Private endpoints (i.e. those prefixed with `pvt_`) require a separate key that needs to be passed as an argument. These endpoints require specific data use agreements to access.
{: .note }

## Basic Usage

To fetch the most recent data for a signal, use `epidata_snapshot()`. This function requires a `source`, `signal` (or `signals`), and a `geo_type`.

Suppose we are interested in emergency department visits for influenza from the `nssp` source across the nation:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
library(epidatr)
library(dplyr)

# Obtain the latest snapshot of influenza ED visits from NSSP for the US
epidata <- epidata_snapshot(
  source = "nssp",
  signals = "pct_ed_visits_influenza",
  geo_type = "nation"
)
head(epidata)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
from epidatpy import EpiDataContext, EpiRange

epidata = EpiDataContext()

# Obtain the latest snapshot of influenza ED visits from NSSP for the US
call = epidata.epidata_snapshot(
    source="nssp",
    signals="pct_ed_visits_influenza",
    geo_type="nation",
)
df = call.df()
print(df.head())
```

  </div>
</div>

`epidata_snapshot()` returns a `tibble` in R and an `EpiDataCall` (convertible to a pandas DataFrame via `.df()`) in Python. Each row represents one observation. The location is given in `geo_value`, the observation date in `reference_time`, publication/release timestamp in `report_time`, and the observation estimate in `value`.

To request signals across states instead of the whole nation, specify `geo_type = "state"`. By default, omitting `geo_values` returns all locations for that geographic level:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Obtain data for all states
epidata_snapshot(
  source = "nssp",
  signals = "pct_ed_visits_influenza",
  geo_type = "state"
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Obtain data for all states
epidata.epidata_snapshot(
    source="nssp",
    signals="pct_ed_visits_influenza",
    geo_type="state",
).df()
```

  </div>
</div>

To filter for specific locations and time ranges, use `geo_values` and `reference_time`:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Obtain data for PA, CA, and FL over a date range
epidata_snapshot(
  source = "nssp",
  signals = "pct_ed_visits_influenza",
  geo_type = "state",
  geo_values = c("pa", "ca", "fl"),
  reference_time = epirange(20240101, 20241231)
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Obtain data for PA, CA, and FL over a date range
epidata.epidata_snapshot(
    source="nssp",
    signals="pct_ed_visits_influenza",
    geo_type="state",
    geo_values=["pa", "ca", "fl"],
    reference_time=EpiRange("2024-01-01", "2024-12-31"),
).df()
```

  </div>
</div>

## Getting Versioned Data

The Epidata API records historical releases, updates, and corrections, allowing researchers to reconstruct exactly what was known at any point in the past.

### Point-in-time Snapshots

To retrieve data as it was known on a specific release date in the past, use `snapshot_date` in `epidata_snapshot()`:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Obtain NSSP influenza data for PA as it was known on 2025-01-01
epidata_snapshot(
  source = "nssp",
  signals = "pct_ed_visits_influenza",
  geo_type = "state",
  geo_values = "pa",
  snapshot_date = "2025-01-01"
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Obtain NSSP influenza data for PA as it was known on 2025-01-01
epidata.epidata_snapshot(
    source="nssp",
    signals="pct_ed_visits_influenza",
    geo_type="state",
    geo_values="pa",
    snapshot_date="2025-01-01",
).df()
```

  </div>
</div>

### Full Revision History

To fetch all revisions across time, use `epidata_archive()`. You can filter reports using `report_time` with range queries or comparison operators (e.g. `<2025-01-01` or `EpiRange`):

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Fetch all revisions for PA reported between Nov 2024 and Jan 2025
epidata_archive(
  source = "nssp",
  signals = "pct_ed_visits_influenza",
  geo_type = "state",
  geo_values = "pa",
  reference_time = epirange(20241001, 20241201),
  report_time = epirange(20241101, 20250101)
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Fetch all revisions for PA reported between Nov 2024 and Jan 2025
epidata.epidata_archive(
    source="nssp",
    signals="pct_ed_visits_influenza",
    geo_type="state",
    geo_values="pa",
    reference_time=EpiRange("2024-10-01", "2024-12-01"),
    report_time=EpiRange("2024-11-01", "2025-01-01"),
).df()
```

  </div>
</div>

> **Note:** Full revision histories can be large. Use `reference_time` or `report_time` constraints.
{: .note }

## Plotting

Because output data is returned as a standard `tibble` (R) or pandas `DataFrame` (Python), you can plot it directly using standard libraries like `ggplot2` or `matplotlib`:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
library(ggplot2)

data <- epidata_snapshot(
  source = "nssp",
  signals = "pct_ed_visits_influenza",
  geo_type = "state",
  geo_values = c("pa", "ca", "fl"),
  reference_time = epirange(20240101, 20241231)
)

ggplot(data, aes(x = reference_time, y = value, color = geo_value)) +
  geom_line(linewidth = 1) +
  labs(
    title = "Influenza ED visits from NSSP (2024)",
    x = "Date",
    y = "% of ED visits",
    color = "State"
  )
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
import matplotlib.pyplot as plt

data = epidata.epidata_snapshot(
    source="nssp",
    signals="pct_ed_visits_influenza",
    geo_type="state",
    geo_values=["pa", "ca", "fl"],
    reference_time=EpiRange("2024-01-01", "2024-12-31"),
).df()

fig, ax = plt.subplots(figsize=(8, 4))
(
    data.pivot_table(values="value", index="reference_time", columns="geo_value")
    .plot(xlabel="Date", ylabel="% of ED visits", ax=ax, linewidth=1.5)
)
ax.set_title("Influenza ED visits from NSSP (2024)")
plt.show()
```

  </div>
</div>

## Discovering Sources and Metadata

To discover what sources, signals, geographic types, and date ranges are available in the V5 API, use `epidata_meta()`:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Discover what a source offers: signals, geo types, and date ranges
meta <- epidata_meta(source = "nssp")
meta$signals
meta$geo_types
meta$reference_time_range

# Or discover all available sources
all_meta <- epidata_meta()
names(all_meta)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Discover what a source offers: signals, geo types, and date ranges
meta = epidata.epidata_meta(source="nssp")
print(meta["signals"])
print(meta["geo_types"])
print(meta["reference_time_range"])

# Or discover all available sources
all_meta = epidata.epidata_meta()
print(sorted(all_meta.keys()))
```

  </div>
</div>

For interactive visual discovery and code generation, browse data streams on [EpiPortal](https://delphi.cmu.edu/epiportal). For runnable API queries and interactive parameter examples, see the [Epidata API Guide](https://delphi.cmu.edu/epidata/v5/guide#start).

---

## Legacy Endpoints (V4 & V3)

> **The legacy V3/V4 endpoints (`pub_covidcast()` and legacy `pub_*` functions) are deprecated in favor of the V5 API.** They stopped receiving new data on September 22, 2026, but remain accessible for querying historical data. See the [V4 to V5 Migration Guide](v5_migration.md).
{: .warning }

For historical COVIDcast queries, `pub_covidcast()` is still available:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="r">R</button>
    <button data-tab="python">Python</button>
  </div>

  <div class="tab-content active" data-tab="r" markdown="1">

```r
# Querying historical COVIDcast data
pub_covidcast(
  source = "fb-survey",
  signals = "smoothed_cli",
  geo_type = "state",
  geo_values = "pa",
  time_type = "day",
  time_values = epirange(20210101, 20210410)
)
```

  </div>
  <div class="tab-content" data-tab="python" markdown="1">

```python
# Querying historical COVIDcast data
epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="state",
    geo_values="pa",
    time_type="day",
    time_values=EpiRange(20210101, 20210410),
).df()
```

  </div>
</div>

## Legacy Clients

Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/), [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R), and [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.js),
but their use is discouraged.

The following samples show how to import each legacy library and fetch Delphi’s COVID-19 Surveillance Streams from Facebook Survey CLI for county `06001` and days `20200401` and `20200405-20200414` (11 days total).

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

