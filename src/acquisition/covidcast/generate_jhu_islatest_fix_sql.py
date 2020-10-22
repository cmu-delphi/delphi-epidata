PARTITION_VARIABLE = 'time_value'
PARTITION_SPLITS = [20200101 + i*100 for i in range(10)] # first day of the month for jan - oct 2020 in YYYYMMDD form
### PARTITION_SPLITS = [1,2] ###


# signal name construction
# NOTE: selecting these (unique) from the database takes 7-8 mins, so reconstructing here for efficiency
signals = []
for case in ('confirmed_', 'deaths_'):
  for period in ('7day_', ''):
    for count in ('cumulative_', 'incidence_'):
      for typ in ('num', 'prop'):
        signals.append(case+period+count+typ)
### signals = ['sig2'] ###

print('''
DROP TEMPORARY TABLE `jhu_islatest_fix`;
CREATE TEMPORARY TABLE `jhu_islatest_fix` (`latest_id` INT(11) NOT NULL, PRIMARY KEY (`latest_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''')

clear_old_queries = []
for partition_index in range(len(PARTITION_SPLITS)+1):
  ge_condition = 'TRUE' if partition_index == 0 else f'`{PARTITION_VARIABLE}` >= {PARTITION_SPLITS[partition_index - 1]}'
  l_condition = 'TRUE' if partition_index == len(PARTITION_SPLITS) else f'`{PARTITION_VARIABLE}` < {PARTITION_SPLITS[partition_index]}'
  partition_condition = f'({ge_condition}) AND ({l_condition})'

  for sig in signals:
    where_clause = "WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='%s' AND %s"  % (sig, partition_condition)
    ### where_clause = "WHERE `source`='src2' AND `time_type`='day' AND `geo_type`='msa' AND `signal`='%s' AND %s"  % (sig, partition_condition) ###

    print('''
INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
''' + where_clause + '''
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);
''')

    clear_old_queries.append("UPDATE `covidcast` SET `is_latest_issue`=0  %s;" % where_clause)

for q in clear_old_queries:
  print(q)

print("UPDATE (SELECT `latest_id` FROM `jhu_islatest_fix`) xxx LEFT JOIN `covidcast` ON `xxx`.`latest_id`=`covidcast`.`id` SET `covidcast`.`is_latest_issue`=1;")

print("DROP TEMPORARY TABLE `jhu_islatest_fix`;")
