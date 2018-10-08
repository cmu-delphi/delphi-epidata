"""
Parses historical versions of the NoroSTAT data-table and updates the
appropriate databases. Currently uses snapshots from the WayBack Machine
(archive.org). A more comprehensive archival service may be mementoweb.org,
which appears to pull from many services that implement the Memento protocol,
including archive.org. Manually downloaded snapshots could be recorded via this
script as well.
"""

# standard library
import re
import os
import time
import collections

# first party
import norostat_sql
import norostat_raw

norostat_sql.ensure_tables_exist()

snapshot_dir = os.path.expanduser("~/norostat_history/wayback/websites/www.cdc.gov/norovirus/reporting/norostat/data-table.html/")
snapshot_version_counter = collections.Counter()
for subdir in os.listdir(snapshot_dir):
  if re.match(r'[0-9]+', subdir) is not None:
    # appears to be snapshot dir
    snapshot_version_counter[subdir] = 0 # register that loop found this snapshot directory
    for norostat_capitalization in ["norostat","noroSTAT"]:
      time.sleep(0.002) # ensure parse times are unique, assuming OS can accurately sleep and measure to ms precision
      path = os.path.join(snapshot_dir,subdir,"norovirus","reporting",norostat_capitalization,"data-table.html")
      if os.path.isfile(path):
        print("Processing file ", path)
        with open(path, 'r') as datatable_file:
          content = datatable_file.read()
        wide_raw = norostat_raw.parse_content_to_wide_raw(content)
        long_raw = norostat_raw.melt_wide_raw_to_long_raw(wide_raw)
        norostat_sql.record_long_raw(long_raw)
        snapshot_version_counter[subdir] += 1
print('Successfully uploaded the following snapshots, with the count indicating the number of data-table versions found inside each snapshot (expected to be 1, or maybe 2 if there was a change in capitalization; 0 indicates the NoroSTAT page was not found within a snapshot directory); just "Counter()" indicates no snapshot directories were found:', snapshot_version_counter)

norostat_sql.update_point()
