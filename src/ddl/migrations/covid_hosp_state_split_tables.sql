-- 1. Add new state_daily table mirroring state_timeseries table

CREATE TABLE `covid_hosp_state_daily` (
  -- for uniqueness
  PRIMARY KEY (`id`),
  -- for fast lookup of most recent issue for a given state and date
  UNIQUE KEY `issue_by_state_and_date` (`state`, `date`, `issue`),
  -- for fast lookup of a time-series for a given state and issue
  KEY `date_by_issue_and_state` (`issue`, `state`, `date`),
  -- for fast lookup of all states for a given date and issue
  KEY `state_by_issue_and_date` (`issue`, `date`, `state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
SELECT * FROM covid_hosp_state_timeseries WHERE record_type='D';
-- AUTOINCREMENT is not preserved by `CREATE TABLE ... SELECT`; Re-add
ALTER TABLE covid_hosp_state_daily MODIFY id INT NOT NULL AUTO_INCREMENT;

-- 2. Remove data with incorrect record_type from timeseries table (D records were moved to daily)

DELETE FROM `covid_hosp_state_timeseries` WHERE record_type='D';

-- 3. Remove the record_type column from both tables

ALTER TABLE `covid_hosp_state_daily` DROP COLUMN record_type;
ALTER TABLE `covid_hosp_state_timeseries` DROP COLUMN record_type;
