
DROP TEMPORARY TABLE `jhu_islatest_fix`;
CREATE TEMPORARY TABLE `jhu_islatest_fix` (`latest_id` INT(11) NOT NULL, PRIMARY KEY (`latest_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (TRUE) AND (`time_value` < 20200101)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);


INSERT INTO `jhu_islatest_fix`
  SELECT id FROM
    ( SELECT `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, MAX(`issue`) AS `issue` FROM `covidcast`
WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE)
      GROUP BY `source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`);

UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (TRUE) AND (`time_value` < 20200101);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200101) AND (`time_value` < 20200201);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200201) AND (`time_value` < 20200301);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200301) AND (`time_value` < 20200401);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200401) AND (`time_value` < 20200501);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200501) AND (`time_value` < 20200601);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200601) AND (`time_value` < 20200701);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200701) AND (`time_value` < 20200801);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200801) AND (`time_value` < 20200901);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20200901) AND (`time_value` < 20201001);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_7day_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='confirmed_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_7day_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_cumulative_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_num' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE `covidcast` SET `is_latest_issue`=0  WHERE `source`='jhu-csse' AND `time_type`='day' AND `geo_type`='state' AND `signal`='deaths_incidence_prop' AND (`time_value` >= 20201001) AND (TRUE);
UPDATE (SELECT `latest_id` FROM `jhu_islatest_fix`) xxx LEFT JOIN `covidcast` ON `xxx`.`latest_id`=`covidcast`.`id` SET `covidcast`.`is_latest_issue`=1;
DROP TEMPORARY TABLE `jhu_islatest_fix`;
