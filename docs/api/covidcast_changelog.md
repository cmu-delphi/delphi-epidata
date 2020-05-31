# Delphi's COVID-19 Surveillance Streams Changelog

When Delphi makes substantial changes to the computation of a signal, we will typically publish it under a new name rather than revising the existing signal. By contrast, the changes documented here are bug fixes and pipeline repairs.

## Sources and Signals
### `doctor-visits`
### `fb-survey`

<a name="fb-survey-v1.3"></a> 
#### 3 June 2020: v1.3

Duplicate survey weights had corrupted historical figures for the following signals and dates. The correct data has been restored to the API.
* `raw_wcli`
  * `county`: 20200406, 20200408, 20200410, 20200430
  * `hrr`: 20200406, 20200408-20200410, 20200430
  * `msa`: 20200408, 20200410, 20200430
  * `state`: 20200408-20200410, 20200430
* `smoothed_wcli`
  * `county`: 20200406, 20200408-20200414, 20200430-20200506
  * `hrr`: 20200406-20200415, 20200430-20200506
  * `msa`: 20200408-20200414, 20200430-20200506
  * `state`: 20200408-20200416, 20200430-20200506

### `google-survey`
### `ght`
### `quidel`
### `jhu-csse`
### `indicator-combination`
