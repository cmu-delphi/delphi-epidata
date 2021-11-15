select_sql = f'''
    SELECT 
        ref.`geo_value`, ref.`signal`, ref.`source`, ref.`geo_type`, ref.`time_type`, ref.`time_value`, data.`issue`, 
        data.`lag`, data.`missing_value`, data.`missing_stderr`, data.`missing_sample_size`, data.`value`, 
        data.`stderr`, data.`sample_size` 
    FROM data_reference ref
    INNER JOIN datapoint data
    ON ref.`latest_datapoint_id` = data.`id` 
    WHERE 
        ((ref.`source` = "jhu-csse" AND (ref.`signal` = "deaths_incidence_prop"))) AND 
        ((ref.`geo_type` = "county" AND (ref.`geo_value` = 01001))) AND (ref.`time_type` = "day")
    ORDER BY 
        ref.`source` ASC, ref.`signal` ASC, ref.`time_type` ASC, ref.`time_value` ASC, ref.`geo_type` ASC, 
        ref.`geo_value` ASC, data.`issue` ASC
'''

trend_sql = f'''
    SELECT ref.`geo_type`, ref.`geo_value`, ref.`source`, ref.`signal`, ref.`time_value`, data.`value`
    FROM data_reference ref
    INNER JOIN datapoint data
    ON ref.`latest_datapoint_id` = data.`id`
    WHERE 
        ((ref.`source` = "jhu-csse" AND (ref.`signal` = "deaths_incidence_prop"))) AND 
        ((ref.`geo_type` = "county" AND (ref.`geo_value` = 01001))) AND 
        ((ref.`time_type` = "day" AND (ref.`time_value` BETWEEN 20200122 AND 20200122)))
    ORDER BY ref.`geo_type` ASC, ref.`geo_value` ASC, ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

trend_series_sql = f'''
    SELECT ref.`geo_type`, ref.`geo_value`, ref.`source`, ref.`signal`, ref.`time_value`, data.`value`
    FROM data_reference ref
    INNER JOIN datapoint data
    ON ref.`latest_datapoint_id` = data.`id`
    WHERE 
        ((ref.`source` = "jhu-csse" AND (ref.`signal` = "deaths_incidence_prop"))) AND 
        ((ref.`geo_type` = "county" AND (ref.`geo_value` = 01001))) AND
        ((ref.`time_type` = "day" AND (ref.`time_value` BETWEEN 20200122 AND 20200122)))
    ORDER BY ref.`geo_type` ASC, ref.`geo_value` ASC, ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

correlation_sql = f'''
    SELECT ref.`geo_type`, ref.`geo_value`, ref.`source`, ref.`signal`, ref.`time_value`, data.`value` 
    FROM data_reference ref
    INNER JOIN datapoinet data
    ON ref.`latest_datapoint_id` = data.`id`  
    WHERE 
        ((ref.`source` = "jhu-csse" AND (ref.`signal` = "deaths_incidence_prop")) OR (ref.`source` = "jhu-csse" AND 
        (ref.`signal` = "deaths_incidence_prop"))) AND ((ref.`geo_tgit ype` = "county" AND (ref.`geo_value` = 01001))) AND 
        ((ref.`time_type` = "day" AND (ref.`time_value` BETWEEN 20200122 AND 20200122))) 
    ORDER BY ref.`geo_type` ASC, ref.`geo_value` ASC, ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

coverage_sql = f'''
    SELECT ref.`source`, ref.`signal`, ref.`time_value`, COUNT(ref.`geo_value`) AS count 
    FROM data_reference ref
    INNER JOIN datapoint data
    ON ref.`latest_datapoint_id` = data.`id`
    WHERE 
        ref.`geo_type` = "county" AND ((ref.`source` = "jhu-csse" AND (ref.`signal` = "deaths_incidence_prop"))) AND 
        ((ref.`time_type` = "day" AND (ref.`time_value` BETWEEN 20200122 AND 20200122))) 
    GROUP BY ref.`source`, ref.`signal`, ref.`time_value` 
    ORDER BY ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

coverage_sql = '''SELECT 
count(ref.`geo_value`) as count, ref.`source`, ref.`signal`, ref.`time_value`, 
FROM 
data_reference ref 
WHERE (ref.`source` = "jhu-csse" AND
ref.`signal` = "deaths_incidence_prop") AND
ref.`geo_type` = "county" AND
ref.`time_type` = "day" AND
ref.`time_value` BETWEEN x and y AND
ORDER BY
ref.`source` ASC,
ref.`signal` ASC,
data.`time_value` ASC'''

backfill_sql = '''SELECT
ref.time_value, 
data.issue, 
data.value, 
data.sample_size 
FROM 
data_reference ref
INNER JOIN datapoint data 
ON ref.latest_datapoint_id = data.id
WHERE ref.source = :source_0t AND 
ref.signal = :signal AND 
ref.geo_type = :geo_type AND 
ref.geo_value = :geo_Type AND 
ref.time_type = :time_type AND 
ref.time_value BETWEEN :time_x AND :time_y
ORDER BY 
ref.time_value ASC, 
data.issue ASC
'''

csv_sql = '''SELECT ref.geo_value
ref.signal
ref.time_value
data.issue
data.lag
data.value
data.stderr,
data.sample_size,
FROM data_reference
INNER JOIN datapoint data
ON ref.latest_datapoint_id = data.id
WHERE ref.source = :source AND
ref.signal = :signal AND
ref.time_type = :time_type AND
ref.time_value = BETWEEN :time x AND :time y AND
ref.geo_type = :geo_type
ORDER BY ref.time_value ASC,
ref.geo_value ASC'''

meta_sql = '''SELECT epidata FROM covidcast_meta_cache'''
