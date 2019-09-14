# first party
from . import afhsb_sql, afhsb_csv, afhsb_utils

def main():
    # afhsb_csv.aggregate_and_process()
    afhsb_sql.init_all_tables_with_issue(metadatapath=afhsb_utils.SOURCE_DIR, datapath=afhsb_utils.TARGET_DIR, criterion="flucat")

if __name__ == '__main__':
    main()
