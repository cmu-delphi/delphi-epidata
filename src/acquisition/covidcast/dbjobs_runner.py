
from delphi.epidata.acquisition.covidcast.database import Database

# simple helper to easily run dbjobs from the command line, such as after an acquisition cycle is complete

def main():
  database = Database()
  database.connect()
  try:
    database.run_dbjobs()
  finally:
    database.disconnect(True)

if __name__ == '__main__':
  main()
