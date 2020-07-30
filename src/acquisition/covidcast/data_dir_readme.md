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

Automation will periodically (currently at :50 every hour) check for new files
nested under `receiving/`.  When it finds some, it will upload them to the
epidata database and then archive the source CSV as described above. The API
will immediately begin serving the new data.

## data spec

Criteria for a valid filename:

- Name format is `YYYYMMDD_{geo}_{signal}.csv` for dailies and
  `weekly_YYYYWW_{geo}_{signal}.csv` for weeklies
- Minimum year: 2019
- Maximum year: 2030
- `geo` one of: county, hrr, msa, dma, state
- `signal` must be matched by a `/\w+/` regex. If you do not want this signal to
  be surfaced in the metadata information, the signal name should start with
  `wip_`.

If a filename is invalid, it does not get ingested, and will be listed in the
failed archive.

Criteria for a valid file:

- Required columns in header: `geo_id`,`val`,`se`,`sample_size`
- Additional columns are permitted but will be ignored
- `geo_id` for `hrr`, `msa`, `dma` must be interpretable as a `/[0-9]+/` string
  (ints and floats are allowed but you definitely want to be careful there)
- `geo_id` for `county` must have length 5 and sort between '01000' and '80000'
- `geo_id` for `hrr` must sort between '001' and '500'
- `geo_id` for `msa` must have length 5 and sort between '10000' and'99999'
- `geo_id` for `dma` must sort between '450' and '950'
- `geo_id` for `state` must have length 2 and sort between 'aa' and 'zz'
- `value` must be a real number (ie not nan, inf, empty, na, or None)
- `se` may be nan; if it is a number, it must be nonnegative
- `sample_size` may be nan; if it is a number, it must be at least 5

If a file has invalid headers, it does not get ingested, and will be listed in
the failed archive.

If a row has invalid data, the **row** is skipped, but the rest of the file is
ingested. The file will be listed in the failed archive.

If a filename is valid and all data in the file is valid, it will be listed in
the successful archive.

## administrators guide

To add a new source, create a directory in `receiving/` with permissions that
exactly match the other directories there. The easiest way to do this is to `cp -a`
a directory from an existing source that happens to be empty.

You do not need to create a directory in `archive/successful` or
`archive/failed`; one will be created automatically as soon as it is needed. Do
not modify the permissions in the archive directories, as a permissions error
will crash the data ingestion job.

The reason for each failed file is logged by Automation in the ~automation
directory. Off-cycle ingestions can be scheduled using the Automation web
console.
