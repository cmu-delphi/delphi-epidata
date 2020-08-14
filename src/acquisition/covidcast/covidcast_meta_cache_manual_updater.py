"""Updates the cache for the `covidcast_meta` endpoint by reading JSON out of a file"""

import argparse
import json
import sys

from delphi.epidata.acquisition.covidcast.database import Database


def get_argument_parser():
    """Define command line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=str)
    return parser

def main(args, database_impl=Database):
    """Read metadata out of a JSON file and use that to update the meta cache.

    File format accepts either the JSON that would be returned from a
    metadata call (ie a dict with keys [result, message, epidata]) or
    the JSON that is cached in the table (ie a list of dicts, one dict
    per signal configuration)
    """
    meta = {}
    with open(args.metadata) as new_metadata:
        meta = json.load(new_metadata)
    if isinstance(meta, dict):
        if "epidata" in meta:
            meta = meta['epidata']
    if not isinstance(meta, list):
        print("Bad metadata type: expected list, got {type(meta)}")
        sys.exit(1)

    database = database_impl()
    database.connect()

    try:
        database.update_covidcast_meta_cache(json.dumps(meta))
        print('successfully cached epidata')
    finally:
        database.disconnect(True)
    return True

if __name__ == '__main__':
    if not main(get_argument_parser().parse_args()):
        sys.exit(1)
