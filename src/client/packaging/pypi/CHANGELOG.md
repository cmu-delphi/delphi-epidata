# Changelog

All notable future changes to the `delphi_epidata` python client will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/).

## [4.1.25] - 2024-07-18

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1456

### Changed
- Added a one-time check which logs a warning when the newest client version does not match the client version in use.

## [4.1.24] - 2024-07-09

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1470
- https://github.com/cmu-delphi/delphi-epidata/pull/1486
- https://github.com/cmu-delphi/delphi-epidata/pull/1463
- https://github.com/cmu-delphi/delphi-epidata/pull/1465

### Changed
- Replaced `setup.py` with `pyproject.toml` for package metadata and build configuration.
- Removed heavy `delphi_utils` dependency by changing debug output from structured logger to direct stderr printing.

### Fixed
- Resolved previous version number typo in CHANGELOG.
- Client version will now only incremented and released when there are structural/functional changes. 

## [4.1.23] - 2024-05-31

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1460

### Fixed
- Replaced bad internal logger package import with one from `delphi_utils` package instead.
  - This bug affected releases 4.1.21 and 4.1.22

## [4.1.21] - 2024-05-20

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1418
- https://github.com/cmu-delphi/delphi-epidata/pull/1436

### Added
- Adds two debug flags:
  - `debug` logs info about HTTP requests and responses
  - `sandbox` prevents any HTTP requests from actually executing, allowing for tests that do not incur server load.
- Fixes the `user-agent` version so that it is correctly set to match the current client release.

## [4.1.17] - 2024-01-30

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1363

### Changed
- Replaced use of deprecated setuptools' `pkg_resources` library with the native `importlib.metadata` library.

## [4.1.13] - 2023-11-04

### Includes
- https://github.com/cmu-delphi/delphi-epidata/pull/1323
- https://github.com/cmu-delphi/delphi-epidata/pull/1330

### Changed
- Appends a trailing slash to URLs requested by the Python client, which should prevent an automatic redirect and an extra request to the server.

### Removed
- Removed the `covidcast_nowcast()` method, as the associated API endpoint is no longer available.

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
