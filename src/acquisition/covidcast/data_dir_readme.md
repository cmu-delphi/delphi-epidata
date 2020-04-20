# covidcast data directory

NOTE: Edit this file on GitHub!
https://github.com/cmu-delphi/delphi-epidata/tree/master/src/acquisition/covidcast/data_dir_readme.md

This is the location where covidcast CSVs are deposited and stored.

## layout

**WARNING: All data herein is publicly surfaced through the Epidata API.**

There are three important directories:

- `receiving/`: put your new CSVs under a subdirectory here!
- `archive/successful/`: storage for successfully uploaded CSVs. automation
  will compress and move your CSVs here.
- `archive/failed/`: storage for broken or failed CSVs. automation will move
  your uncompressed CSVs here for you to debug. delete them when you're
  finished. consult automation logs to determine the reason for the failure.

Within each of the above, there are a number of subdirectories, generally one
for each covidcast data source. It's important to place your CSVs in the
appropriate subdirectory as the name of the data source is extracted from the
path of each file.

Any files that are unable to be loaded due to invalid naming will be moved to
the special directory `archive/failed/unknown/`, as in this case the data
source name (i.e. name of subdirectory) is not assumed to be reliable.

## handling

Automation will periodically check for new files nested under `receiving/`.
When it finds some, it will upload them to the epidata database and then
archive the source CSV as described above. The API will immediately begin
serving the new data.
