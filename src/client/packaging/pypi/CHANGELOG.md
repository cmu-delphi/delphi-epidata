# Changelog

All notable future changes to the `delphi_epidata` python client will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/).

## [4.1.11] - 2023-10-12

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1288

### Changed
- Internally uses newer endpoint-specific URLs instead of an older compatibility alias URL.
- Upper limit on the number of rows returned per request has been increased to 1M (was 3650).
- Method `Epidata.async_epidata()` is now deprecated and will be removed in a future version.
- The dict object returned from data request methods will now always have an entry for the "`epidata`" key, potentially with an empty list as its value.  previously, if there were no results for the request, the "`epidata`" entry was not present.
- Results from the `Epidata.covidcast()` method (or potentially the `covidcast` endpoint via the `async_epidata()` method) will now include the keys "`source`", "`geo_type`", and "`time_type`" (and their associated values).

## [4.1.10] - 2023-09-28

### Added
- Established this Changelog
