# standard library
import os

# third party
import mysql.connector as connector

# first party
import delphi.operations.secrets as secrets

def init_raw_data(table_name, sourcefile):
    print("Initialize {}".format(table_name))
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    create_table_cmd = '''
        CREATE TABLE IF NOT EXISTS `{}` (
        `id` INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
        `epiweek` INT(6) NOT NULL,
        `dmisid` CHAR(4) NULL,
        `flu_severity` INT(1) NOT NULL,
        `visit_sum` INT(11) NOT NULL,
        
        KEY `epiweek` (`epiweek`),
        KEY `dmisid` (`dmisid`),
        KEY `flu_severity` (`flu_severity`)
        );
        '''.format(table_name)
    populate_table_cmd = '''
        LOAD DATA INFILE '{}' 
        INTO TABLE {}
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        IGNORE 1 ROWS
        (@id, @epiweek, @dmisid, @flu, @visits)
        SET 
            id = @id,
            epiweek = @epiweek,
            dmisid = nullif(@dmisid, 'ZZZZ'),
            flu_severity = @flu,
            visit_sum = @visits
        ;
        '''.format(sourcefile, table_name)
    try:
        cursor = cnx.cursor()
        cursor.execute(create_table_cmd)
        cursor.execute(populate_table_cmd)
        cnx.commit()
    finally:
        cnx.close()

def init_dmisid_table(sourcefile):
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    table_name = 'dmisid_table'
    create_table_cmd = '''
        CREATE TABLE `{}` (
        `dmisid` INT(4) NOT NULL PRIMARY KEY,
        `country` CHAR(2) NULL,
        `state` CHAR(2) NULL
        );
        '''.format(table_name)
    populate_table_cmd = '''
        LOAD DATA INFILE '{}' 
        INTO TABLE {}
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        IGNORE 1 ROWS
        (@dmisid, @country, @state, @zip5)
        SET    
            dmisid = @dmisid,
            country = nullif(@country, ''),
            state = nullif(@state, '')
        ;
	'''.format(sourcefile, table_name)
    try:
        cursor = cnx.cursor()
        cursor.execute(create_table_cmd)
        cursor.execute(populate_table_cmd)
        cnx.commit()
    finally:
        cnx.close()

def agg_by_state(src_table, dest_table):
    print("Aggregating records by state...")
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    cmd = '''
        CREATE TABLE {}
        SELECT a.epiweek, a.flu_severity, d.state, d.country, sum(a.visit_sum) visit_sum
        FROM {} a
        LEFT JOIN dmisid_table d 
        ON a.dmisid = d.dmisid 
        GROUP BY a.epiweek, a.flu_severity, d.state, d.country;
    '''.format(dest_table, src_table)
    try:
        cursor = cnx.cursor()
        cursor.execute(cmd)
        cnx.commit()
    finally:
        cnx.close()

def init_all_tables(datapath):
    init_dmisid_table("/simple_DMISID_FY2018.csv")

    periods = ["00to13", "13to17"]
    for period in periods:
        table_name = "afhsb_{}_raw".format(period)
        init_raw_data(table_name, os.path.join(datapath, "{}.csv".format(period)))
        agg_by_state(table_name, 'afhsb_{}_state'.format(period))

def run_cmd(cmd):
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    try:
        cursor = cnx.cursor()
        cursor.execute(cmd)
        cnx.commit()
    finally:
        cnx.close()

if __name__ == '__main__':
    init_all_tables("/")