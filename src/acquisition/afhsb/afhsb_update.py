# first party
from . import afhsb_sql, afhsb_csv, afhsb_utils

def main():
    afhsb_csv.aggregate_and_process()
    afhsb_sql.init_all_tables(TARGET_DIR)

if __name__ == '__main__':
    main()