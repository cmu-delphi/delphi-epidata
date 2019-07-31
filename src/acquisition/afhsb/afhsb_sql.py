# standard library
import os

# third party
import mysql.connector as connector

# first party
import delphi.operations.secrets as secrets


def init_dmisid_table(sourcefile):
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    table_name = 'dmisid_table'
    create_table_cmd = '''
        CREATE TABLE `{}` (
        `dmisid` INT(4) NOT NULL PRIMARY KEY,
        `country` CHAR(3) NULL,
        `state` CHAR(2) NULL
        );
        '''.format(table_name)
    populate_table_cmd = '''
        LOAD DATA LOCAL INFILE '{}' 
        INTO TABLE {}
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"'
        LINES TERMINATED BY '\r\n'
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

def init_region_table(sourcefile):
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    table_name = 'state2region_table'
    create_table_cmd = '''
        CREATE TABLE `{}` (
        `state` CHAR(2) NOT NULL PRIMARY KEY,
        `hhs` CHAR(5) NOT NULL,
        `cen` CHAR(4) NOT NULL
        );
        '''.format(table_name)
    populate_table_cmd = '''
        LOAD DATA LOCAL INFILE '{}' 
        INTO TABLE {}
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"'
        LINES TERMINATED BY '\r\n'
        IGNORE 1 ROWS
        (@state, @hhs, @cen)
        SET state=@state, hhs=@hhs, cen=@cen;
	'''.format(sourcefile, table_name)
    try:
        cursor = cnx.cursor()
        cursor.execute(create_table_cmd)
        cursor.execute(populate_table_cmd)
        cnx.commit()
    finally:
        cnx.close()


def init_raw_data(table_name, sourcefile):
    print("Initialize {}".format(table_name))
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    create_table_cmd = '''
        CREATE TABLE IF NOT EXISTS `{}` (
        `id` INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
        `epiweek` INT(6) NOT NULL,
        `dmisid` CHAR(4) NULL,
        `flu_type` CHAR(9) NOT NULL,
        `visit_sum` INT(11) NOT NULL,
        
        KEY `epiweek` (`epiweek`),
        KEY `dmisid` (`dmisid`),
        KEY `flu_type` (`flu_type`)
        );
        '''.format(table_name)
    populate_table_cmd = '''
        LOAD DATA LOCAL INFILE '{}' 
        INTO TABLE {}
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"'
        LINES TERMINATED BY '\r\n'
        IGNORE 1 ROWS
        (@id, @epiweek, @dmisid, @flu, @visits)
        SET 
            id = @id,
            epiweek = @epiweek,
            dmisid = nullif(@dmisid, 'ZZZZ'),
            flu_type = @flu,
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

def agg_by_state(src_table, dest_table):
    print("Aggregating records by states...")
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    cmd = '''
        CREATE TABLE {}
        SELECT a.epiweek, a.flu_type, d.state, d.country, sum(a.visit_sum) visit_sum
        FROM {} a
        LEFT JOIN dmisid_table d 
        ON a.dmisid = d.dmisid 
        GROUP BY a.epiweek, a.flu_type, d.state, d.country;
    '''.format(dest_table, src_table)
    try:
        cursor = cnx.cursor()
        cursor.execute(cmd)
        cnx.commit()
    finally:
        cnx.close()

def agg_by_region(src_table, dest_table):
    print("Aggregating records by regions...")
    (u, p) = secrets.db.epi
    cnx = connector.connect(user=u, passwd=p, database="epidata")
    cmd = '''
        CREATE TABLE {}
        SELECT s.epiweek, s.flu_type, r.hhs, r.cen, sum(s.visit_sum) visit_sum
        FROM {} s
        LEFT JOIN state2region_table r
        ON s.state = r.state
        GROUP BY s.epiweek, s.flu_type, r.hhs, r.cen;
    '''.format(dest_table, src_table)
    try:
        cursor = cnx.cursor()
        cursor.execute(cmd)
        cnx.commit()
    finally:
        cnx.close()

def init_all_tables(datapath):
    init_dmisid_table(os.path.join(datapath, "simple_DMISID_FY2018.csv"))
    init_region_table(os.path.join(datapath, "state2region.csv"))

    periods = ["00to13", "13to17"]
    for period in periods:
        raw_table_name = 'afhsb_{}_raw'.format(period)
        state_table_name = 'afhsb_{}_state'.format(period)
        region_table_name = 'afhsb_{}_region'.format(period)
        
        init_raw_data(raw_table_name, os.path.join(datapath, "filled_{}.csv".format(period)))
        agg_by_state(raw_table_name, state_table_name)
        agg_by_region(state_table_name, region_table_name)

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