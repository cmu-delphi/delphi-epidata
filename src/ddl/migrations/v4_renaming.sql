-- drop VIEWs in `epidata` that act as aliases to (ie, they reference) VIEWs in `covid`
USE epidata;
DROP VIEW
    signal_history_v,
    signal_latest_v;

-- return to v4 schema namespace
USE covid;

-- drop VIEWs that reference main TABLEs
DROP VIEW
    signal_history_v,
    signal_latest_v;

-- rename main TABLEs
RENAME TABLE
    signal_history TO epimetric_full,
    signal_latest  TO epimetric_latest,
    signal_load    TO epimetric_load;

-- rename id COLUMNs in main TABLEs
ALTER TABLE epimetric_full   RENAME COLUMN signal_data_id TO epimetric_id;
ALTER TABLE epimetric_latest RENAME COLUMN signal_data_id TO epimetric_id;
ALTER TABLE epimetric_load   RENAME COLUMN signal_data_id TO epimetric_id;

-- -- -- TODO: rename `value_key_*` INDEXes in `epimetric_*` TABLEs to `???_idx_*`?

-- re-create VIEWs that reference newly renamed TABLEs (this is a straight copy of the VIEW definitions from ../v4_schema.sql
CREATE OR REPLACE VIEW epimetric_full_v AS
    SELECT
        0 AS `is_latest_issue`, -- provides column-compatibility to match `covidcast` table
        -- ^ this value is essentially undefined in this view, the notion of a 'latest' issue is not encoded here and must be drawn from the 'latest' table or view or otherwise computed...
        NULL AS `direction`, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`epimetric_id` AS `epimetric_id`,
        `t1`.`strat_key_id` AS `strat_key_id`, -- TODO: for future use
        `t1`.`issue` AS `issue`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`time_type` AS `time_type`,
        `t1`.`time_value` AS `time_value`,
        `t1`.`reference_dt` AS `reference_dt`, -- TODO: for future use
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`,
        `t1`.`geo_key_id` AS `geo_key_id`
    FROM `epimetric_full` `t1`
        JOIN `signal_dim` `t2`
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`
        JOIN `geo_dim` `t3`
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`;
CREATE OR REPLACE VIEW epimetric_latest_v AS
    SELECT
        1 AS `is_latest_issue`, -- provides column-compatibility to match `covidcast` table
        NULL AS `direction`, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`epimetric_id` AS `epimetric_id`,
        `t1`.`strat_key_id` AS `strat_key_id`, -- TODO: for future use
        `t1`.`issue` AS `issue`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`time_type` AS `time_type`,
        `t1`.`time_value` AS `time_value`,
        `t1`.`reference_dt` AS `reference_dt`, -- TODO: for future use
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`,
        `t1`.`geo_key_id` AS `geo_key_id`
    FROM `epimetric_latest` `t1`
        JOIN `signal_dim` `t2`
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`
        JOIN `geo_dim` `t3`
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`;


-- re-create `epidata` alias VIEWs
USE epidata;
CREATE VIEW epidata.epimetric_full_v   AS SELECT * FROM covid.epimetric_full_v;
CREATE VIEW epidata.epimetric_latest_v AS SELECT * FROM covid.epimetric_latest_v;
