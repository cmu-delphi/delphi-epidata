# first party
from . import afhsb_sql

DATAPATH = '/home/automation/afhsb_data'

def main():
    afhsb_sql.init_all_tables(DATAPATH)

if __name__ == '__main__':
    main()
