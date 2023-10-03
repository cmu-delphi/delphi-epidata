# Changelog

All notable future changes to the `delphi_epidata` python client will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/).

## [4.2.0] - 2023-09-27

### Changed
 
- Modify the signatures for several methods: endpoint no longer needs to be specified in the params dict under the "source" key, but becomes a mandatory parameter for the method:
  - `async_epidata(param_list, batch_size=50)` → `async_epidata(endpoint, param_list, batch_size=50)`

## [4.1.10] - 2023-09-28

### Added
- Established this Changelog
