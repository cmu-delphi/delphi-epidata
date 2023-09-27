# Change Log
All notable changes to this client will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [4.2.0] - 2023-09-27
  
### Added

### Changed
 
- Modify the signatures for several methods: endpoint no longer needs to be specified in the params dict under the "source" key, but becomes a mandatory parameter for the method:
  - `_request(params)` → `_request(endpoint, params={})`
  - `_request_with_retry(params)` → `_request_with_retry(endpoint, params={})`
  - `async_epidata(param_list, batch_size=50)` → `async_epidata(endpoint, param_list, batch_size=50)`

### Fixed
 