# what data to operate on
base_where_clause = "WHERE `source`='jhu-csse' AND `time_type`='day'"
### base_where_clause = "WHERE `source`='src2' AND `time_type`='day'" ###


# signal name construction
# NOTE: selecting these (unique) from the database takes 7-8 mins, so reconstructing here for efficiency
# TODO: maybe just put the damn UNIQUE query in here so you dont fat-finger it again george.
#       also these hardcoded signals are unique to JHU data, or are at least not used by all sources.
signals = []
for case in ('confirmed_', 'deaths_'):
  for period in ('7dav_', ''): # NOTE: that is a V as in "7 Day AVerage", not a "Y" as in "7 DAY"
    for count in ('cumulative_', 'incidence_'):
      for typ in ('num', 'prop'):
        signals.append(case+period+count+typ)
### signals = ['sig2'] ###


# variable to split on, 'time_value' is good because its high cardinality is suitable for chunking
PARTITION_VARIABLE = 'time_value'
PARTITION_SPLITS = [20200101 + i*100 for i in range(10)] # first day of the month for jan - oct 2020 in YYYYMMDD form
### PARTITION_SPLITS = [1,2] ###


print('''
-- 
-- run this as:
--   python3 generate_islatest_fix_sql.py > islatest_fix.sql
--   mysql -vvv -p epidata < islatest_fix.sql
-- or:
--   date ; (python3 generate_islatest_fix_sql.py | mysql -vvv -p epidata ) ; date
-- 
''')

# create temp table
print("CREATE TABLE `islatest_fix` (`latest_id` INT(11) NOT NULL, PRIMARY KEY (`latest_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")

# find latest issue by partition (and by signal) and save primary ids into temp table
for partition_index in range(len(PARTITION_SPLITS)+1):
  ge_condition = 'TRUE' if partition_index == 0 else f'`{PARTITION_VARIABLE}` >= {PARTITION_SPLITS[partition_index - 1]}'
  l_condition = 'TRUE' if partition_index == len(PARTITION_SPLITS) else f'`{PARTITION_VARIABLE}` < {PARTITION_SPLITS[partition_index]}'
  partition_condition = f'({ge_condition}) AND ({l_condition})'

  for sig in signals:
    where_clause = base_where_clause + " AND `signal`='%s' AND %s"  % (sig, partition_condition)

    print('''
INSERT INTO `islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
      ''' + where_clause + '''
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);
''')

# clear any current (potentially erroneous) is_latest_issue flags
print("UPDATE `covidcast` SET `is_latest_issue`=0 " + base_where_clause + " AND `is_latest_issue`=1;")

# re-set proper is_latest_issue flags
print("UPDATE (SELECT `latest_id` FROM `islatest_fix`) xxx LEFT JOIN `covidcast` ON `xxx`.`latest_id`=`covidcast`.`id` SET `covidcast`.`is_latest_issue`=1;")

# clean up temp table
print("-- TODO: drop this table")
print("-- DROP TABLE `islatest_fix`;")
