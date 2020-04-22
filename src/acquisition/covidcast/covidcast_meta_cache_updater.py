"""Updates the cache for the `covidcast_meta` endpiont."""

# standard library
import json

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi.epidata.client.delphi_epidata import Epidata


def main():
  response = Epidata.covidcast_meta()
  print(response['result'])

  if response['result'] == 1:
    commit = False
    database = Database()
    database.connect()
    try:
      database.update_covidcast_meta_cache(json.dumps(response['epidata']))
      commit = True
      print('successfully cached epidata')
    finally:
      database.disconnect(commit)
  else:
    print('metadata is not available')


if __name__ == '__main__':
  main()
