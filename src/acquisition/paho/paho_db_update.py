"""
===============
=== Purpose ===
===============

Stores versioned PAHO Dengue data from PAHO website.

=======================
=== Data Dictionary ===
=======================

`paho_dengue` is where the Dengue data from PAHO is stored.

+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date   | date        | NO   | MUL | NULL    |                | 
| issue          | int(11)     | NO   | MUL | NULL    |                |
| epiweek        | int(11)     | NO   | MUL | NULL    |                |
| region         | varchar(12) | NO   | MUL | NULL    |                |
| lag            | int(11)     | NO   | MUL | NULL    |                |
| total_pop      | int(11)     | NO   |     | NULL    |                |
| serotype       | numchar(12) | NO   |     | NULL    |                |
| num_dengue     | int(11)     | YES  |     | NULL    |                |
| incidence_rate | double      | YES  |     | NULL    |                |
| num_severe     | int(11)     | YES  |     | NULL    |                |
| num_deaths     | int(11)     | YES  |     | NULL    |                |
+----------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
  and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
region: the name of the location (3 letter country code)
lag: number of weeks between `epiweek` and `issue`
total_pop: population of country in thousands
serotype: identified dengue serotype
num_dengue: cumulative cases of dengue in calendar year
incidence_rate: (num_dengue/total_pop) * 100
num_severe: cumulative cases of severe dengue in calendar year
num_deaths: cumulative deaths in calendar year
"""

# TODO: small countries have names not recognized by pycountry
#       could hardcode them
# TODO: Obviously regions not recognized by pycountry
#       Should be aggregated and therefore redundant, maybe hardcode them

import argparse
import csv
import datetime
import glob
import random
import subprocess
from io import StringIO

import delphi.operations.secrets as secrets
import mysql.connector
import pycountry
from delphi.epidata.acquisition.paho.paho_download import get_paho_data
from delphi.utils.epidate import EpiDate
from delphi.utils.epiweek import check_epiweek, delta_epiweeks


def ensure_tables_exist():
    (u, p) = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database='epidata')
    try:
        cursor = cnx.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS `paho_dengue` (
                `id` INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                `release_date` DATE NOT NULL,
                `issue` INT(11) NOT NULL,
                `epiweek` INT(11) NOT NULL,
                `lag` INT(11) NOT NULL,
                `region` VARCHAR(12) NOT NULL,
                `total_pop` INT(11) NOT NULL,
                `serotype` VARCHAR(12) NOT NULL,
                `num_dengue` INT(11) NOT NULL,
                `incidence_rate` DOUBLE NOT NULL,
                `num_severe` INT(11) NOT NULL,
                `num_deaths` INT(11) NOT NULL,
                UNIQUE KEY (`issue`, `epiweek`, `region`)
            );
        ''')
        cnx.commit()
    finally:
        cnx.close()


def safe_float(f):
    try:
        return float(f.replace(',',''))
    except:
        return 0


def safe_int(i):
    try:
        return int(i.replace(',',''))
    except:
        return 0


def get_rows(cnx, table='paho_dengue'):
    # Count and return the number of rows in the `fluview` table.
    select = cnx.cursor()
    select.execute('SELECT count(1) num FROM %s' % table)
    for (num,) in select:
        pass
    select.close()
    return num


def get_paho_row(row):
    if row[0] == "\ufeffIncidence Rate (c)" and row != "\ufeffIncidence Rate (c),(SD/D) x100 (e),CFR (f),ID,Country or Subregion,Deaths,EW,Confirmed,Epidemiological Week (a),Pop (no usar),Serotype,Severe Dengue (d),Total of Dengue Cases (b),Year,Population x 1000".split(","): # noqa
        raise Exception('PAHO header row has changed')
    if len(row) == 1 or row[0] == "Incidence Rate (c)":
        # this is a header row
        return None
    try:
        country = pycountry.countries.get(name=row[4]).alpha_2
    except:
        try:
            country = pycountry.countries.get(common_name=row[4]).alpha_2
        except:
            try:
                country = pycountry.countries.get(official_name=row[4]).alpha_2
            except:
                return None
    try:
        check_epiweek(safe_int(row[13])*100 + safe_int(row[8]), safe_int(row[13])*100 + safe_int(row[6]))
    except:
        return None
    return {
        'issue': safe_int(row[13])*100 + safe_int(row[6]),
        'epiweek': safe_int(row[13])*100 + safe_int(row[8]),
        'region': country,
        'total_pop': safe_int(row[14]),
        'serotype': row[10],
        'num_dengue': safe_int(row[12]),
        'incidence_rate': safe_float(row[0]),
        'num_severe': safe_int(row[11]),
        'num_deaths': safe_int(row[5]),
        'severe_ratio': safe_float(row[1]),
        'cfr': safe_float(row[2])
    }


def update_from_file(issue, date, filename, test_mode=False):
    # Read PAHO data from CSV and insert into (or update) the database.

    # Behavior with issue:
    # PAHO has drop down menu for week, and selecting a given week
    #   from that menu gives the data for that issue, not that EW
    # Unsure what revisions, if any, that data goes through
    # Current code ignores PAHO-given issue, is based on argument 'issue'

    # database connection
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database='epidata')
    rows1 = get_rows(cnx, 'paho_dengue')
    print('rows before: %d' % (rows1))
    insert = cnx.cursor()

    # load the data, ignoring empty rows
    print('loading data from %s as issued on %d' % (filename, issue))
    with open(filename, 'r', encoding='utf-8') as f:
        c = f.read()
    rows = []
    for l in csv.reader(StringIO(c), delimiter=','):  # noqa
        rows.append(get_paho_row(l))
    print(' loaded %d rows' % len(rows))
    entries = [obj for obj in rows if obj]
    print(' found %d entries' % len(entries))

    sql = '''
    INSERT INTO
        `paho_dengue` (`release_date`, `issue`, `epiweek`, `region`, `lag`,
        `total_pop`, `serotype`, `num_dengue`, `incidence_rate`,
        `num_severe`, `num_deaths`)
    VALUES
        ('%s', %s, %s, '%s', %s, %s, '%s', %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        `release_date` = least(`release_date`, '%s'),
        `total_pop` = %s,
        `serotype` = '%s',
        `num_dengue` = %s,
        `incidence_rate` = %s,
        `num_severe` = %s,
        `num_deaths` = %s
    '''

    for row in entries:
        if row['issue'] > issue:  # Issued in a week that hasn't happened yet
            continue
        lag = delta_epiweeks(row['epiweek'], issue)
        data_args = [row['total_pop'], row['serotype'], row['num_dengue'],
                     row['incidence_rate'], row['num_severe'], row['num_deaths']]

        insert_args = [date, issue, row['epiweek'], row['region'], lag] + data_args
        update_args = [date] + data_args
        insert.execute(sql % tuple(insert_args + update_args))

    # cleanup
    insert.close()
    if test_mode:
        print('test mode, not committing')
        rows2 = rows1
    else:
        cnx.commit()
        rows2 = get_rows(cnx)
    print('rows after: %d (added %d)' % (rows2, rows2-rows1))
    cnx.close()


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--test',
        action='store_true',
        help='do dry run only, do not update the database'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='load an existing zip file (otherwise fetch current data)'
    )
    parser.add_argument(
        '--issue',
        type=int,
        help='issue of the file (e.g. 201740); used iff --file is given'
    )
    args = parser.parse_args()

    if (args.file is None) != (args.issue is None):
        raise Exception('--file and --issue must both be present or absent')

    date = datetime.datetime.now().strftime('%Y-%m-%d')
    print('assuming release date is today, %s' % date)

    if args.file:
        update_from_file(args.issue, date, args.file, test_mode=args.test)
    else:
        # Code doesn't always download all files, unreproducible errors
        # Try a few times and hopefully one will work
        ensure_tables_exist()
        flag = 0
        max_tries = 5
        while flag < max_tries:
            flag = flag + 1
            tmp_dir = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(8))
            tmp_dir = 'downloads_' + tmp_dir
            subprocess.call(["mkdir", tmp_dir])
            # Use temporary directory to avoid data from different time
            #   downloaded to same folder
            get_paho_data(dir=tmp_dir)
            issue = EpiDate.today().get_ew()
            # Check to make sure we downloaded a file for every week
            issueset = set()
            files = glob.glob('%s/*.csv' % tmp_dir)
            for filename in files:
                with open(filename, 'r') as f:
                    _ = f.readline()
                    data = f.readline().split(',')
                    issueset.add(data[6])
            db_error = False
            if len(issueset) >= 53:  # Shouldn't be more than 53
                for filename in files:
                    try:
                        update_from_file(issue, date, filename, test_mode=args.test)
                        subprocess.call(["rm", filename])
                    except:
                        db_error = True
                subprocess.call(["rm", "-r", tmp_dir])
                if not db_error:
                    break  # Exit loop with success
            if flag >= max_tries:
                print('WARNING: Database `paho_dengue` did not update successfully')


if __name__ == '__main__':
    main()
