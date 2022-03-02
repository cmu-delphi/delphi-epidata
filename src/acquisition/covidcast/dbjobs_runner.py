
from delphi.epidata.acquisition.covidcast.database import Database

def main():
  database = Database()
  database.connect()
  try:
    database.run_dbjobs()
  finally:
    database.disconnect(True)

if __name__ == '__main__':
  main()
