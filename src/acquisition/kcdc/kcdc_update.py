"""
===============
=== Purpose ===
===============

Stores versioned KCDC ILI data from KCDC website.

=======================
=== Data Dictionary ===
=======================

`kcdc_ili` is where the ILI data from KCDC is stored.
+--------------+-------------+------+-----+---------+----------------+
| Field        | Type        | Null | Key | Default | Extra          |
+--------------+-------------+------+-----+---------+----------------+
| id           | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date | date        | NO   | MUL | NULL    |                |
| issue        | int(11)     | NO   | MUL | NULL    |                |
| epiweek      | int(11)     | NO   | MUL | NULL    |                |
| region       | varchar(12) | NO   | MUL | NULL    |                |
| lag          | int(11)     | NO   | MUL | NULL    |                |
| ili          | double      | YES  |     | NULL    |                |
+--------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
  and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
region: the name of the location (3 letter country code)
lag: number of weeks between `epiweek` and `issue`
ili: num_ili / 1000 outpatient visits
"""

import argparse
import datetime
import requests

# third party
import mysql.connector

# first party
import delphi.operations.secrets as secrets
from delphi.utils.epiweek import delta_epiweeks, range_epiweeks, add_epiweeks
from delphi.utils.epidate import EpiDate
from delphi.epidata.common.logger import get_structured_logger

logger = get_structured_logger("kcdc_update")


def ensure_tables_exist():
    (u, p) = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata")
    try:
        cursor = cnx.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `kcdc_ili` (
                `id` INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                `release_date` DATE NOT NULL,
                `issue` INT(11) NOT NULL,
                `epiweek` INT(11) NOT NULL,
                `lag` INT(11) NOT NULL,
                `region` VARCHAR(12) NOT NULL,
                `ili` DOUBLE NOT NULL,
                UNIQUE KEY (`issue`, `epiweek`, `region`)
            );
            """
        )
        cnx.commit()
    finally:
        cnx.close()


def safe_float(f):
    try:
        return float(f.replace(",", ""))
    except:
        return 0


def safe_int(i):
    try:
        return int(i.replace(",", ""))
    except:
        return 0


def get_rows(cnx, table="kcdc_ili"):
    # Count and return the number of rows in the `kcdc_ili` table.
    select = cnx.cursor()
    select.execute(f"SELECT count(1) num FROM {table}")
    for (num,) in select:
        pass
    select.close()
    return num


def get_kcdc_data():
    issue = EpiDate.today().get_ew()
    last_season = issue // 100 + (1 if issue % 100 > 35 else 0)
    url = "https://www.cdc.go.kr/npt/biz/npp/iss/influenzaListAjax.do"
    # Started in 2004
    params = {
        "icdNm": "influenza",
        "startYear": "2004",
        "endYear": str(last_season),
    }
    response = requests.post(url, params)
    datas = response.json()
    data = datas["data"]
    ews = []
    ilis = []
    ew1 = 200436
    for year in range(2004, last_season):
        year_data = data[year - 2004]
        if year > 2004:
            ew1 = ews[-1] + 1
        ili_yr = year_data["VALUE"].split("`")
        ili_yr = [float(f) for f in ili_yr if f != ""]
        ew2 = add_epiweeks(ew1, len(ili_yr))
        new_ews = list(range_epiweeks(ew1, ew2))
        for i in range(len(new_ews)):
            j = float(ili_yr[i])
            ilis.append(j)
            ews.append(new_ews[i])
    return ews, ilis


def update_from_data(ews, ilis, date, issue, test_mode=False):
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata")
    rows1 = get_rows(cnx)
    logger.info(f"rows before: {int(rows1)}")
    insert = cnx.cursor()

    sql = """
    INSERT INTO
        `kcdc_ili` (`release_date`, `issue`, `epiweek`, `region`, `lag`,
        `ili`)
    VALUES
        ('%s', %s, %s, '%s', %s, %s)
    ON DUPLICATE KEY UPDATE
        `release_date` = least(`release_date`, '%s'),
        `ili` = %s
    """

    for i in range(len(ews)):
        ew = ews[i]
        ili = ilis[i]
        lag = delta_epiweeks(ews[i], issue)

        insert_args = [date, issue, ew, "ROK", lag, ili]
        update_args = [date, ili]
        try:
            insert.execute(sql % tuple(insert_args + update_args))
        except Exception:
            pass

    # cleanup
    insert.close()
    if test_mode:
        logger.info("test mode, not committing")
        rows2 = rows1
    else:
        cnx.commit()
        rows2 = get_rows(cnx)
    logger.info(f"rows after: {int(rows2)} (added {int(rows2 - rows1)})")
    cnx.close()


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="do dry run only, do not update the database"
    )
    args = parser.parse_args()

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    logger.info(f"assuming release date is today, {date}")
    issue = EpiDate.today().get_ew()

    ensure_tables_exist()

    ews, ilis = get_kcdc_data()

    update_from_data(ews, ilis, date, issue, test_mode=args.test)


if __name__ == "__main__":
    main()
