select_old_sql = '''
    SELECT 
        t.geo_value, t.signal, t.source, t.geo_type, t.time_type, t.time_value, t.direction, t.issue, t.lag, 
        t.missing_value, t.missing_stderr, t.missing_sample_size, t.value, t.stderr, t.sample_size 
    FROM covidcast t 
    WHERE 
        ((t.source = "jhu-csse" AND (t.signal = "deaths_incidence_prop"))) AND 
        ((t.geo_type = "county" AND (t.geo_value = 01001))) AND (t.time_type = "day") AND (t.is_latest_issue IS TRUE)  
    ORDER BY t.source ASC, t.signal ASC, t.time_type ASC, t.time_value ASC, t.geo_type ASC, t.geo_value ASC, t.issue ASC LIMIT 3651
'''

select_sql = '''
    SELECT 
        ref.`geo_value`, ref.`signal`, ref.`source`, ref.`geo_type`, ref.`time_type`, ref.`time_value`, point.`issue`, 
        point.`lag`, point.`missing_value`, point.`missing_stderr`, point.`missing_sample_size`, point.`value`, 
        point.`stderr`, point.`sample_size` 
    FROM data_reference ref
    INNER JOIN datapoint point
    ON ref.`latest_datapoint_id` = point.`id` 
    WHERE 
        ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop" AND ref.`geo_type` = "county" AND
        ref.`geo_value` = 01001 AND ref.`time_type` = "day"
    ORDER BY 
        ref.`source` ASC, ref.`signal` ASC, ref.`time_type` ASC, ref.`time_value` ASC, ref.`geo_type` ASC, 
        ref.`geo_value` ASC, point.`issue` ASC
'''

old_trend_sql = '''
    SELECT t.geo_type, t.geo_value, t.source, t.signal, t.time_value, t.value 
    FROM covidcast t  
    WHERE 
        ((t.source = "jhu-csse" AND (t.signal = "deaths_incidence_prop"))) AND 
        ((t.geo_type = "county" AND (t.geo_value = 01001))) AND 
        ((t.time_type = "day" AND (t.time_value BETWEEN 20211005 AND 20211020))) AND (t.is_latest_issue IS TRUE)  
    ORDER BY t.geo_type ASC, t.geo_value ASC, t.source ASC, t.signal ASC, t.time_value ASC
'''

trend_sql = '''
    SELECT ref.`geo_type`, ref.`geo_value`, ref.`source`, ref.`signal`, ref.`time_value`, point.`value`
    FROM data_reference ref
    INNER JOIN datapoint point
    ON ref.`latest_datapoint_id` = point.`id`
    WHERE 
        ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop" AND ref.`geo_type` = "county" AND 
        ref.`geo_value` = 01001 AND ref.`time_type` = "day" AND ref.`time_value` BETWEEN 20211005 AND 20211020
    ORDER BY ref.`geo_type` ASC, ref.`geo_value` ASC, ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

old_trend_series_sql = '''
    SELECT t.geo_type, t.geo_value, t.source, t.signal, t.time_value, t.value 
    FROM covidcast t   
    WHERE 
        ((t.source = "jhu-csse" AND (t.signal = "deaths_incidence_prop"))) AND 
        ((t.geo_type = "county" AND (t.geo_value = 01001))) AND 
        ((t.time_type = "day" AND (t.time_value BETWEEN 20211005 AND 20211020))) AND (t.is_latest_issue IS TRUE)  
    ORDER BY t.geo_type ASC, t.geo_value ASC, t.source ASC, t.signal ASC, t.time_value ASC
'''

trend_series_sql = '''
    SELECT ref.`geo_type`, ref.`geo_value`, ref.`source`, ref.`signal`, ref.`time_value`, point.`value`
    FROM data_reference ref
    INNER JOIN datapoint point
    ON ref.`latest_datapoint_id` = point.`id`
    WHERE 
        ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop" AND ref.`geo_type` = "county" AND 
        ref.`geo_value` = 01001 AND ref.`time_type` = "day" AND ref.`time_value` BETWEEN 20211005 AND 20211020
    ORDER BY ref.`geo_type` ASC, ref.`geo_value` ASC, ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

old_correlation_sql = '''
    SELECT t.geo_type, t.geo_value, t.source, t.signal, t.time_value, t.value FROM covidcast t   
    WHERE 
        ((t.source = "jhu-csse" AND (t.signal = "deaths_incidence_prop")) OR (t.source = "jhu-csse" AND 
        (t.signal = "deaths_incidence_prop"))) AND ((t.geo_type = "county" AND (t.geo_value = 01001))) AND 
        ((t.time_type = "day" AND (t.time_value BETWEEN 20211005 AND 20211020))) AND (t.is_latest_issue IS TRUE)  
    ORDER BY t.geo_type ASC, t.geo_value ASC, t.source ASC, t.signal ASC, t.time_value ASC LIMIT 10000001
'''

correlation_sql = '''
    SELECT ref.`geo_type`, ref.`geo_value`, ref.`source`, ref.`signal`, ref.`time_value`, point.`value` 
    FROM data_reference ref
    INNER JOIN datapoint point
    ON ref.`latest_datapoint_id` = point.`id`  
    WHERE 
        ((ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop") OR 
        (ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop")) AND ref.`geo_type` = "county" AND 
        ref.`geo_value` = 01001 AND ref.`time_type` = "day" AND ref.`time_value` BETWEEN 20211005 AND 20211020
    ORDER BY ref.`geo_type` ASC, ref.`geo_value` ASC, ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

old_coverage_sql = '''
    SELECT c.source, c.signal, c.time_value, COUNT(c.geo_value) as count 
    FROM covidcast c   
    WHERE 
        c.geo_type = "county" AND ((c.source = "jhu-csse" AND (c.signal = "deaths_incidence_prop"))) AND 
        ((c.time_type = "day" AND (c.time_value BETWEEN 20211005 AND 20211020))) AND (c.is_latest_issue IS TRUE) 
    GROUP BY c.source, c.signal, c.time_value ORDER BY c.source ASC, c.signal ASC, c.time_value ASC LIMIT 10000001
'''

coverage_sql = '''
    SELECT ref.`source`, ref.`signal`, ref.`time_value`, COUNT(ref.`geo_value`) AS count 
    FROM data_reference ref
    INNER JOIN datapoint point
    ON ref.`latest_datapoint_id` = point.`id`
    WHERE 
        ref.`geo_type` = "county" AND ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop" AND 
        ref.`time_type` = "day" AND ref.`time_value` BETWEEN 20211005 AND 20211020
    GROUP BY ref.`source`, ref.`signal`, ref.`time_value` 
    ORDER BY ref.`source` ASC, ref.`signal` ASC, ref.`time_value` ASC
'''

old_backfill_sql = '''
    SELECT t.time_value, t.issue, t.value, t.sample_size, t.is_latest_issue 
    FROM covidcast t   
    WHERE 
        ((t.source = "jhu-csse" AND (t.signal = "deaths_incidence_prop"))) AND 
        ((t.geo_type = "county" AND (t.geo_value = 01001))) AND 
        ((t.time_type = "day" AND (t.time_value BETWEEN 20211005 AND 20211020))) 
    ORDER BY t.time_value ASC, t.issue ASC LIMIT 10000001
'''

backfill_sql = '''
    SELECT 
        ref.`time_value`, data.`issue`, data.`value`, data.`sample_size`, 
        CASE WHEN ref.`latest_datapoint_id` = data.`id` THEN 1 ELSE 0 END AS `is_latest_issue`
    FROM data_reference ref
    INNER JOIN datapoint data
    ON data.`data_reference_id` = ref.`id`
    WHERE
        ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop" AND ref.`geo_type` = "county" AND 
        ref.`geo_value` = 01001 AND ref.`time_type` = "day" AND ref.`time_value` BETWEEN 20211005 AND 20211020
    ORDER BY ref.`time_value` ASC, data.`issue` ASC
'''

old_csv_sql = '''
    SELECT t.geo_value, t.signal, t.time_value, t.issue, t.lag, t.value, t.stderr, t.sample_size, t.geo_type, t.source 
    FROM covidcast t  
    WHERE 
        ((t.source = "jhu-csse" AND (t.signal = "deaths_incidence_prop"))) AND ((t.time_type = "day" AND 
        (t.time_value BETWEEN 20211005 AND 20211020))) AND (t.geo_type = "county") AND (t.is_latest_issue IS TRUE)  
    ORDER BY t.time_value ASC, t.geo_value ASC LIMIT 10000001
'''

csv_sql = '''
    SELECT 
        ref.`geo_value`, ref.`signal`, ref.`time_value`, point.`issue`, point.`lag`, point.`value`, point.`stderr`, 
        point.`sample_size`, ref.`geo_type`, ref.`source`
    FROM data_reference ref
    INNER JOIN datapoint point
    ON ref.`latest_datapoint_id` = point.`id`
    WHERE 
        ref.`source` = "jhu-csse" AND ref.`signal` = "deaths_incidence_prop" AND ref.`time_type` = "day" AND 
        ref.`time_value` BETWEEN 20211005 AND 20211020 AND (ref.`geo_type` = "county")
    ORDER BY ref.`time_value` ASC, ref.`geo_value` ASC
'''

meta_sql = '''SELECT epidata FROM covidcast_meta_cache'''