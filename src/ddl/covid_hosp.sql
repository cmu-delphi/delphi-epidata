/*
These tables store the collection of datasets relating to COVID-19 patient
impact and hospital capacity. Data is provided by the US Department of Health &
Human Services via healthdata.gov.

For more information, see:
- https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-state-timeseries
- https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-facility
- src/acquisition/covid_hosp/README.md
.
*/


/*
`covid_hosp_meta` stores metadata about all datasets.

Data is public. However, it will likely only be used internally and will not be
surfaced through the Epidata API.

+----------------------+---------------+------+-----+---------+----------------+
| Field                | Type          | Null | Key | Default | Extra          |
+----------------------+---------------+------+-----+---------+----------------+
| id                   | int(11)       | NO   | PRI | NULL    | auto_increment |
| dataset_name         | varchar(64)   | NO   | MUL | NULL    |                |
| publication_date     | int(11)       | NO   |     | NULL    |                |
| revision_timestamp   | varchar(512)  | NO   |     | NULL    |                |
| metadata_json        | longtext      | NO   |     | NULL    |                |
| acquisition_datetime | datetime      | NO   |     | NULL    |                |
+----------------------+---------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `publication_date`
  the day (YYYYMMDD) that the dataset was published
- `dataset_name`
  name of the type of this dataset (e.g. "state_timeseries", "facility")
- `revision_timestamp`
  free-form text field indicating when the dataset was last revised; will
  generally contain some type of timestamp, although the format is not
  well-defined. copied from the metadata object.
- `metadata_json`
  a JSON blob containing verbatim metadata as returned by healthdata.gov
- `acquisition_datetime`
  datetime when the dataset was acquired by delphi
*/

CREATE TABLE `covid_hosp_meta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dataset_name` VARCHAR(64) NOT NULL,
  `publication_date` INT NOT NULL,
  `revision_timestamp` VARCHAR(512) NOT NULL,
  `metadata_json` JSON NOT NULL,
  `acquisition_datetime` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of a particular revision for a specific dataset
  UNIQUE KEY (`dataset_name`, `revision_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*
`covid_hosp_state_timeseries` stores the versioned "state timeseries" dataset,
which contains data from both the time series data and the daily snapshot files.

Data is public under the Open Data Commons Open Database License (ODbL).

+------------------------------------------------------------------+---------+------+-----+---------+----------------+
| Field                                                            | Type    | Null | Key | Default | Extra          |
+------------------------------------------------------------------+---------+------+-----+---------+----------------+
| id                                                               | int(11) | NO   | PRI | NULL    | auto_increment |
| issue                                                            | int(11) | NO   | MUL | NULL    |                |
| state                                                            | char(2) | NO   | MUL | NULL    |                |
| date                                                             | int(11) | NO   |     | NULL    |                |
| critical_staffing_shortage_today_yes                             | int(11) | YES  |     | NULL    |                |
| critical_staffing_shortage_today_no                              | int(11) | YES  |     | NULL    |                |
| critical_staffing_shortage_today_not_reported                    | int(11) | YES  |     | NULL    |                |
| critical_staffing_shortage_anticipated_within_week_yes           | int(11) | YES  |     | NULL    |                |
| critical_staffing_shortage_anticipated_within_week_no            | int(11) | YES  |     | NULL    |                |
| critical_staffing_shortage_anticipated_within_week_not_reported  | int(11) | YES  |     | NULL    |                |
| hospital_onset_covid                                             | int(11) | YES  |     | NULL    |                |
| hospital_onset_covid_coverage                                    | int(11) | YES  |     | NULL    |                |
| inpatient_beds                                                   | int(11) | YES  |     | NULL    |                |
| inpatient_beds_coverage                                          | int(11) | YES  |     | NULL    |                |
| inpatient_beds_used                                              | int(11) | YES  |     | NULL    |                |
| inpatient_beds_used_coverage                                     | int(11) | YES  |     | NULL    |                |
| inpatient_beds_used_covid                                        | int(11) | YES  |     | NULL    |                |
| inpatient_beds_used_covid_coverage                               | int(11) | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed                     | int(11) | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_coverage            | int(11) | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected                     | int(11) | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_coverage            | int(11) | YES  |     | NULL    |                |
| previous_day_admission_pediatric_covid_confirmed                 | int(11) | YES  |     | NULL    |                |
| previous_day_admission_pediatric_covid_confirmed_coverage        | int(11) | YES  |     | NULL    |                |
| previous_day_admission_pediatric_covid_suspected                 | int(11) | YES  |     | NULL    |                |
| previous_day_admission_pediatric_covid_suspected_coverage        | int(11) | YES  |     | NULL    |                |
| staffed_adult_icu_bed_occupancy                                  | int(11) | YES  |     | NULL    |                |
| staffed_adult_icu_bed_occupancy_coverage                         | int(11) | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_suspected_covid             | int(11) | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_suspected_covid_coverage    | int(11) | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_covid                       | int(11) | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_covid_coverage              | int(11) | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_suspected_covid              | int(11) | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_suspected_covid_coverage     | int(11) | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_covid                        | int(11) | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_covid_coverage               | int(11) | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_suspected_covid          | int(11) | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_suspected_covid_coverage | int(11) | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_covid                    | int(11) | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_covid_coverage           | int(11) | YES  |     | NULL    |                |
| total_staffed_adult_icu_beds                                     | int(11) | YES  |     | NULL    |                |
| total_staffed_adult_icu_beds_coverage                            | int(11) | YES  |     | NULL    |                |
| inpatient_beds_utilization                                       | double  | YES  |     | NULL    |                |
| inpatient_beds_utilization_coverage                              | int(11) | YES  |     | NULL    |                |
| inpatient_beds_utilization_numerator                             | int(11) | YES  |     | NULL    |                |
| inpatient_beds_utilization_denominator                           | int(11) | YES  |     | NULL    |                |
| percent_of_inpatients_with_covid                                 | double  | YES  |     | NULL    |                |
| percent_of_inpatients_with_covid_coverage                        | int(11) | YES  |     | NULL    |                |
| percent_of_inpatients_with_covid_numerator                       | int(11) | YES  |     | NULL    |                |
| percent_of_inpatients_with_covid_denominator                     | int(11) | YES  |     | NULL    |                |
| inpatient_bed_covid_utilization                                  | double  | YES  |     | NULL    |                |
| inpatient_bed_covid_utilization_coverage                         | int(11) | YES  |     | NULL    |                |
| inpatient_bed_covid_utilization_numerator                        | int(11) | YES  |     | NULL    |                |
| inpatient_bed_covid_utilization_denominator                      | int(11) | YES  |     | NULL    |                |
| adult_icu_bed_covid_utilization                                  | double  | YES  |     | NULL    |                |
| adult_icu_bed_covid_utilization_coverage                         | int(11) | YES  |     | NULL    |                |
| adult_icu_bed_covid_utilization_numerator                        | int(11) | YES  |     | NULL    |                |
| adult_icu_bed_covid_utilization_denominator                      | int(11) | YES  |     | NULL    |                |
| adult_icu_bed_utilization                                        | double  | YES  |     | NULL    |                |
| adult_icu_bed_utilization_coverage                               | int(11) | YES  |     | NULL    |                |
| adult_icu_bed_utilization_numerator                              | int(11) | YES  |     | NULL    |                |
| adult_icu_bed_utilization_denominator                            | int(11) | YES  |     | NULL    |                |
| record_type                                                      | char(1) | NO   | MUL | NULL    |                |
+------------------------------------------------------------------+---------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `issue`
  the day (YYYYMMDD) that the dataset was published
- `date`
  the day (YYYYMMDD) to which the data applies

NOTE: Names have been shortened to 64 characters, as this is a technical
limitation of the database. Affected names are:

staffed_icu_adult_patients_confirmed_and_suspected_covid ->
  staffed_icu_adult_patients_confirmed_suspected_covid
staffed_icu_adult_patients_confirmed_and_suspected_covid_coverage ->
  staffed_icu_adult_patients_confirmed_suspected_covid_coverage
total_adult_patients_hospitalized_confirmed_and_suspected_covid ->
  total_adult_patients_hosp_confirmed_suspected_covid
total_adult_patients_hospitalized_confirmed_and_suspected_covid_coverage ->
  total_adult_patients_hosp_confirmed_suspected_covid_coverage
total_adult_patients_hospitalized_confirmed_covid ->
  total_adult_patients_hosp_confirmed_covid
total_adult_patients_hospitalized_confirmed_covid_coverage ->
  total_adult_patients_hosp_confirmed_covid_coverage
total_pediatric_patients_hospitalized_confirmed_and_suspected_covid ->
  total_pediatric_patients_hosp_confirmed_suspected_covid
total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_coverage ->
  total_pediatric_patients_hosp_confirmed_suspected_covid_coverage
total_pediatric_patients_hospitalized_confirmed_covid ->
  total_pediatric_patients_hosp_confirmed_covid
total_pediatric_patients_hospitalized_confirmed_covid_coverage ->
  total_pediatric_patients_hosp_confirmed_covid_coverage

NOTE: the following data dictionary is copied from
https://healthdata.gov/covid-19-reported-patient-impact-and-hospital-capacity-state-data-dictionary
version entitled "November 18, 2020 release 2.4".

- `state`
  The two digit state code
- `critical_staffing_shortage_today_yes`
  Number of hospitals reporting a critical staffing shortage today in this state.
- `critical_staffing_shortage_today_no`
  Number of hospitals reporting as not having a critical staffing shortage today
  in this state.
- `critical_staffing_shortage_today_not_reported`
  Number of hospitals not reporting staffing shortage today status in this state.
- `critical_staffing_shortage_anticipated_within_week_yes`
  Number of hospitals reporting that they anticipate a critical staffing shortage
  within a week in this state.
- `critical_staffing_shortage_anticipated_within_week_no`
  Number of hospitals reporting that they do not anticipate a critical staffing
  shortage within a week in this state.
- `critical_staffing_shortage_anticipated_within_week_not_reported`
  Number of hospitals not reporting staffing shortage within week status in this state.
- `hospital_onset_covid`
  Total current inpatients with onset of suspected or laboratory-confirmed
  COVID-19 fourteen or more days after admission for a condition other than
  COVID-19 in this state.
- `hospital_onset_covid_coverage`
  Number of hospitals reporting "hospital_onset_covid" in this state
- `inpatient_beds`
  Reported total number of staffed inpatient beds including all overflow and
  surge/expansion beds used for inpatients (includes all ICU beds) in this
  state
- `inpatient_beds_coverage`
  Number of hospitals reporting "inpatient_beds" in this state
- `inpatient_beds_used`
  Reported total number of staffed inpatient beds that are occupied in this
  state
- `inpatient_beds_used_coverage`
  Number of hospitals reporting "inpatient_beds_used" in this state
- `inpatient_beds_used_covid`
  Reported patients currently hospitalized in an inpatient bed who have
  suspected or confirmed COVID-19 in this state
- `inpatient_beds_used_covid_coverage`
  Number of hospitals reporting "inpatient_beds_used_covid" in this state
- `previous_day_admission_adult_covid_confirmed`
  Number of patients who were admitted to an adult inpatient bed on the
  previous calendar day who had confirmed COVID-19 at the time of admission in
  this state
- `previous_day_admission_adult_covid_confirmed_coverage`
  Number of hospitals reporting "previous_day_admission_adult_covid_confirmed"
  in this state
- `previous_day_admission_adult_covid_suspected`
  Number of patients who were admitted to an adult inpatient bed on the
  previous calendar day who had suspected COVID-19 at the time of admission in
  this state
- `previous_day_admission_adult_covid_suspected_coverage`
  Number of hospitals reporting "previous_day_admission_adult_covid_suspected"
  in this state
- `previous_day_admission_pediatric_covid_confirmed`
  Number of pediatric patients who were admitted to an inpatient bed, including
  NICU, PICU, newborn, and nursery, on the previous calendar day who had
  confirmed COVID-19 at the time of admission in this state
- `previous_day_admission_pediatric_covid_confirmed_coverage`
  Number of hospitals reporting
  "previous_day_admission_pediatric_covid_confirmed" in this state
- `previous_day_admission_pediatric_covid_suspected`
  Number of pediatric patients who were admitted to an inpatient bed, including
  NICU, PICU, newborn, and nursery, on the previous calendar day who had
  suspected COVID-19 at the time of admission in this state
- `previous_day_admission_pediatric_covid_suspected_coverage`
  Number of hospitals reporting
  "previous_day_admission_pediatric_covid_suspected" in this state
- `staffed_adult_icu_bed_occupancy`
  Reported total number of staffed inpatient adult ICU beds that are occupied
  in this state
- `staffed_adult_icu_bed_occupancy_coverage`
  Number of hospitals reporting "staffed_adult_icu_bed_occupancy" in this state
- `staffed_icu_adult_patients_confirmed_and_suspected_covid`
  Reported patients currently hospitalized in an adult ICU bed who have
  suspected or confirmed COVID-19 in this state
- `staffed_icu_adult_patients_confirmed_and_suspected_covid_coverage`
  Number of hospitals reporting
  "staffed_icu_adult_patients_confirmed_and_suspected_covid" in this state
- `staffed_icu_adult_patients_confirmed_covid`
  Reported patients currently hospitalized in an adult ICU bed who have
  confirmed COVID-19 in this state
- `staffed_icu_adult_patients_confirmed_covid_coverage`
  Number of hospitals reporting "staffed_icu_adult_patients_confirmed_covid" in
  this state
- `total_adult_patients_hospitalized_confirmed_and_suspected_covid`
  Reported patients currently hospitalized in an adult inpatient bed who have
  laboratory-confirmed or suspected COVID-19. This include those in observation
  beds.
- `total_adult_patients_hospitalized_confirmed_and_suspected_covid_coverage`
  Number of hospitals reporting
  "total_adult_patients_hospitalized_confirmed_and_suspected_covid" in this
  state
- `total_adult_patients_hospitalized_confirmed_covid`
  Reported patients currently hospitalized in an adult inpatient bed who have
  laboratory-confirmed COVID-19. This include those in observation beds.
- `total_adult_patients_hospitalized_confirmed_covid_coverage`
  Number of hospitals reporting
  "total_adult_patients_hospitalized_confirmed_covid" in this state
- `total_pediatric_patients_hospitalized_confirmed_and_suspected_covid`
  Reported patients currently hospitalized in a pediatric inpatient bed,
  including NICU, newborn, and nursery, who are suspected or
  laboratory-confirmed-positive for COVID-19. This include those in observation
  beds.
- `total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_coverage`
  Number of hospitals reporting
  "total_pediatric_patients_hospitalized_confirmed_and_suspected_covid" in this
  state
- `total_pediatric_patients_hospitalized_confirmed_covid`
  Reported patients currently hospitalized in a pediatric inpatient bed,
  including NICU, newborn, and nursery, who are laboratory-confirmed-positive
  for COVID-19. This include those in observation beds.
- `total_pediatric_patients_hospitalized_confirmed_covid_coverage`
  Number of hospitals reporting
  "total_pediatric_patients_hospitalized_confirmed_covid" in this state
- `total_staffed_adult_icu_beds`
  Reported total number of staffed inpatient adult ICU beds in this state
- `total_staffed_adult_icu_beds_coverage`
  Number of hospitals reporting "total_staffed_adult_icu_beds" in this state
- `inpatient_beds_utilization`
  Percentage of inpatient beds that are being utilized in this state. This
  number only accounts for hospitals in the state that report both
  "inpatient_beds_used" and "inpatient_beds" fields.
- `inpatient_beds_utilization_coverage`
  Number of hospitals reporting both "inpatient_beds_used" and "inpatient_beds"
- `inpatient_beds_utilization_numerator`
  Sum of "inpatient_beds_used" for hospitals reporting both
  "inpatient_beds_used" and "inpatient_beds"
- `inpatient_beds_utilization_denominator`
  Sum of "inpatient_beds" for hospitals reporting both "inpatient_beds_used"
  and "inpatient_beds"
- `percent_of_inpatients_with_covid`
  Percentage of inpatient population who have suspected or confirmed COVID-19
  in this state. This number only accounts for hospitals in the state that
  report both "inpatient_beds_used_covid" and "inpatient_beds_used" fields.
- `percent_of_inpatients_with_covid_coverage`
  Number of hospitals reporting both "inpatient_beds_used_covid" and
  "inpatient_beds_used".
- `percent_of_inpatients_with_covid_numerator`
  Sum of "inpatient_beds_used_covid" for hospitals reporting both
  "inpatient_beds_used_covid" and "inpatient_beds_used".
- `percent_of_inpatients_with_covid_denominator`
  Sum of "inpatient_beds_used" for hospitals reporting both
  "inpatient_beds_used_covid" and "inpatient_beds_used".
- `inpatient_bed_covid_utilization`
  Percentage of total (used/available) inpatient beds currently utilized by
  patients who have suspected or confirmed COVID-19 in this state. This number
  only accounts for hospitals in the state that report both
  "inpatient_beds_used_covid" and "inpatient_beds" fields.
- `inpatient_bed_covid_utilization_coverage`
  Number of hospitals reporting both "inpatient_beds_used_covid" and
  "inpatient_beds".
- `inpatient_bed_covid_utilization_numerator`
  Sum of "inpatient_beds_used_covid" for hospitals reporting both
  "inpatient_beds_used_covid" and "inpatient_beds".
- `inpatient_bed_covid_utilization_denominator`
  Sum of "inpatient_beds" for hospitals reporting both
  "inpatient_beds_used_covid" and "inpatient_beds".
- `adult_icu_bed_covid_utilization`
  Percentage of total staffed adult ICU beds currently utilized by patients who
  have suspected or confirmed COVID-19 in this state. This number only accounts
  for hospitals in the state that report both
  "staffed_icu_adult_patients_confirmed_and_suspected_covid" and
  "total_staffed_adult_icu_beds" fields.
- `adult_icu_bed_covid_utilization_coverage`
  Number of hospitals reporting both both
  "staffed_icu_adult_patients_confirmed_and_suspected_covid" and
  "total_staffed_adult_icu_beds".
- `adult_icu_bed_covid_utilization_numerator`
  Sum of "staffed_icu_adult_patients_confirmed_and_suspected_covid" for
  hospitals reporting both
  "staffed_icu_adult_patients_confirmed_and_suspected_covid" and
  "total_staffed_adult_icu_beds".
- `adult_icu_bed_covid_utilization_denominator`
  Sum of "total_staffed_adult_icu_beds" for hospitals reporting both
  "staffed_icu_adult_patients_confirmed_and_suspected_covid" and
  "total_staffed_adult_icu_beds".
- `adult_icu_bed_utilization`
  Percentage of staffed adult ICU beds that are being utilized in this state.
  This number only accounts for hospitals in the state that report both
  "staffed_adult_icu_bed_occupancy" and "total_staffed_adult_icu_beds" fields.
- `adult_icu_bed_utilization_coverage`
  Number of hospitals reporting both both "staffed_adult_icu_bed_occupancy" and
  "total_staffed_adult_icu_beds".
- `adult_icu_bed_utilization_numerator`
  Sum of "staffed_adult_icu_bed_occupancy" for hospitals reporting both
  "staffed_adult_icu_bed_occupancy" and "total_staffed_adult_icu_beds".
- `adult_icu_bed_utilization_denominator`
  Sum of "total_staffed_adult_icu_beds" for hospitals reporting both
  "staffed_adult_icu_bed_occupancy" and "total_staffed_adult_icu_beds".

NOTES:
There is a `date` column from the time series data which indicates the
date corresponding to the values.
For daily snapshot files, there is a `reporting_cutoff_start` value,
defined as "Look back date start - The latest reports from each hospital
is summed for this report starting with this date." We place this value
into the `date` column.

We also add a column `record_type` that specifies if a row came from a
time series file or a daily snapshot file. "T" = time series and
"D" =  daily snapshot. When both a time series and a daily snapshot row
have the same issue/date/state but different values, we tiebreak by
taking the daily snapshot value. This is done with a window function that
sorts by the record_type field, ascending, and so it is important that "D"
comes before "T".
*/

CREATE TABLE `covid_hosp_state_timeseries` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `issue` INT NOT NULL,
  `state` CHAR(2) NOT NULL,
  `date` INT NOT NULL,
  `critical_staffing_shortage_today_yes` INT,
  `critical_staffing_shortage_today_no` INT,
  `critical_staffing_shortage_today_not_reported` INT,
  `critical_staffing_shortage_anticipated_within_week_yes` INT,
  `critical_staffing_shortage_anticipated_within_week_no` INT,
  `critical_staffing_shortage_anticipated_within_week_not_reported` INT,
  `hospital_onset_covid` INT,
  `hospital_onset_covid_coverage` INT,
  `inpatient_beds` INT,
  `inpatient_beds_coverage` INT,
  `inpatient_beds_used` INT,
  `inpatient_beds_used_coverage` INT,
  `inpatient_beds_used_covid` INT,
  `inpatient_beds_used_covid_coverage` INT,
  `previous_day_admission_adult_covid_confirmed` INT,
  `previous_day_admission_adult_covid_confirmed_coverage` INT,
  `previous_day_admission_adult_covid_suspected` INT,
  `previous_day_admission_adult_covid_suspected_coverage` INT,
  `previous_day_admission_pediatric_covid_confirmed` INT,
  `previous_day_admission_pediatric_covid_confirmed_coverage` INT,
  `previous_day_admission_pediatric_covid_suspected` INT,
  `previous_day_admission_pediatric_covid_suspected_coverage` INT,
  `staffed_adult_icu_bed_occupancy` INT,
  `staffed_adult_icu_bed_occupancy_coverage` INT,
  `staffed_icu_adult_patients_confirmed_suspected_covid` INT,
  `staffed_icu_adult_patients_confirmed_suspected_covid_coverage` INT,
  `staffed_icu_adult_patients_confirmed_covid` INT,
  `staffed_icu_adult_patients_confirmed_covid_coverage` INT,
  `total_adult_patients_hosp_confirmed_suspected_covid` INT,
  `total_adult_patients_hosp_confirmed_suspected_covid_coverage` INT,
  `total_adult_patients_hosp_confirmed_covid` INT,
  `total_adult_patients_hosp_confirmed_covid_coverage` INT,
  `total_pediatric_patients_hosp_confirmed_suspected_covid` INT,
  `total_pediatric_patients_hosp_confirmed_suspected_covid_coverage` INT,
  `total_pediatric_patients_hosp_confirmed_covid` INT,
  `total_pediatric_patients_hosp_confirmed_covid_coverage` INT,
  `total_staffed_adult_icu_beds` INT,
  `total_staffed_adult_icu_beds_coverage` INT,
  `inpatient_beds_utilization` DOUBLE,
  `inpatient_beds_utilization_coverage` INT,
  `inpatient_beds_utilization_numerator` INT,
  `inpatient_beds_utilization_denominator` INT,
  `percent_of_inpatients_with_covid` DOUBLE,
  `percent_of_inpatients_with_covid_coverage` INT,
  `percent_of_inpatients_with_covid_numerator` INT,
  `percent_of_inpatients_with_covid_denominator` INT,
  `inpatient_bed_covid_utilization` DOUBLE,
  `inpatient_bed_covid_utilization_coverage` INT,
  `inpatient_bed_covid_utilization_numerator` INT,
  `inpatient_bed_covid_utilization_denominator` INT,
  `adult_icu_bed_covid_utilization` DOUBLE,
  `adult_icu_bed_covid_utilization_coverage` INT,
  `adult_icu_bed_covid_utilization_numerator` INT,
  `adult_icu_bed_covid_utilization_denominator` INT,
  `adult_icu_bed_utilization` DOUBLE,
  `adult_icu_bed_utilization_coverage` INT,
  `adult_icu_bed_utilization_numerator` INT,
  `adult_icu_bed_utilization_denominator` INT,
  `record_type` CHAR(1) NOT NULL,
  -- new columns added Oct 10
  `geocoded_state` INT,
  `previous_day_admission_adult_covid_confirmed_18-19` INT,
  `previous_day_admission_adult_covid_confirmed_18-19_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_20-29` INT,
  `previous_day_admission_adult_covid_confirmed_20-29_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_30-39` INT,
  `previous_day_admission_adult_covid_confirmed_30-39_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_40-49` INT,
  `previous_day_admission_adult_covid_confirmed_40-49_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_50-59` INT,
  `previous_day_admission_adult_covid_confirmed_50-59_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_60-69` INT,
  `previous_day_admission_adult_covid_confirmed_60-69_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_70-79` INT,
  `previous_day_admission_adult_covid_confirmed_70-79_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_80+` INT,
  `previous_day_admission_adult_covid_confirmed_80+_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_unknown` INT,
  `previous_day_admission_adult_covid_confirmed_unknown_coverage` INT,
  `previous_day_admission_adult_covid_suspected_18-19` INT,
  `previous_day_admission_adult_covid_suspected_18-19_coverage` INT,
  `previous_day_admission_adult_covid_suspected_20-29` INT,
  `previous_day_admission_adult_covid_suspected_20-29_coverage` INT,
  `previous_day_admission_adult_covid_suspected_30-39` INT,
  `previous_day_admission_adult_covid_suspected_30-39_coverage` INT,
  `previous_day_admission_adult_covid_suspected_40-49` INT,
  `previous_day_admission_adult_covid_suspected_40-49_coverage` INT,
  `previous_day_admission_adult_covid_suspected_50-59` INT,
  `previous_day_admission_adult_covid_suspected_50-59_coverage` INT,
  `previous_day_admission_adult_covid_suspected_60-69` INT,
  `previous_day_admission_adult_covid_suspected_60-69_coverage` INT,
  `previous_day_admission_adult_covid_suspected_70-79` INT,
  `previous_day_admission_adult_covid_suspected_70-79_coverage` INT,
  `previous_day_admission_adult_covid_suspected_80+` INT,
  `previous_day_admission_adult_covid_suspected_80+_coverage` INT,
  `previous_day_admission_adult_covid_suspected_unknown` INT,
  `previous_day_admission_adult_covid_suspected_unknown_coverage` INT,
  `deaths_covid` INT,
  `deaths_covid_coverage` INT,
  `on_hand_supply_therapeutic_a_casirivimab_imdevimab_courses` INT,
  `on_hand_supply_therapeutic_b_bamlanivimab_courses` INT,
  `on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses` INT,
  `previous_week_therapeutic_a_casirivimab_imdevimab_courses_used` INT,
  `previous_week_therapeutic_b_bamlanivimab_courses_used` INT,
  `previous_week_therapeutic_c_bamlanivimab_etesevimab_courses_used` INT,
  `icu_patients_confirmed_influenza` INT,
  `icu_patients_confirmed_influenza_coverage` INT,
  `previous_day_admission_influenza_confirmed` INT,
  `previous_day_admission_influenza_confirmed_coverage` INT,
  `previous_day_deaths_covid_and_influenza` INT,
  `previous_day_deaths_covid_and_influenza_coverage` INT,
  `previous_day_deaths_influenza` INT,
  `previous_day_deaths_influenza_coverage` INT,
  `total_patients_hospitalized_confirmed_influenza` INT,
  `total_patients_hospitalized_confirmed_influenza_covid` INT,
  `total_patients_hospitalized_confirmed_influenza_covid_coverage` INT,
  `total_patients_hospitalized_confirmed_influenza_coverage` INT,
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of most recent issue for a given state, date, and record type
  UNIQUE KEY `issue_by_state_and_date` (`state`, `date`, `issue`, `record_type`),
  -- for fast lookup of a time-series for a given state, issue, and record type
  KEY `date_by_issue_and_state` (`issue`, `state`, `date`, `record_type`),
  -- for fast lookup of all states for a given date, issue, and record_type
  KEY `state_by_issue_and_date` (`issue`, `date`, `state`, `record_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*
`covid_hosp_facility` stores the versioned "facility" dataset.

Data is public under the Open Data Commons Open Database License (ODbL).

+------------------------------------------------------------------+--------------+------+-----+---------+----------------+
| Field                                                            | Type         | Null | Key | Default | Extra          |
+------------------------------------------------------------------+--------------+------+-----+---------+----------------+
| id                                                               | int(11)      | NO   | PRI | NULL    | auto_increment |
| publication_date                                                 | int(11)      | NO   | MUL | NULL    |                |
| hospital_pk                                                      | varchar(128) | NO   | MUL | NULL    |                |
| collection_week                                                  | int(11)      | NO   |     | NULL    |                |
| state                                                            | char(2)      | NO   | MUL | NULL    |                |
| ccn                                                              | varchar(20)  | YES  |     | NULL    |                |
| hospital_name                                                    | varchar(256) | YES  |     | NULL    |                |
| address                                                          | varchar(128) | YES  |     | NULL    |                |
| city                                                             | varchar(64)  | YES  |     | NULL    |                |
| zip                                                              | char(5)      | YES  |     | NULL    |                |
| hospital_subtype                                                 | varchar(64)  | YES  |     | NULL    |                |
| fips_code                                                        | char(5)      | YES  |     | NULL    |                |
| is_metro_micro                                                   | tinyint(1)   | YES  |     | NULL    |                |
| total_beds_7_day_avg                                             | double       | YES  |     | NULL    |                |
| all_adult_hospital_beds_7_day_avg                                | double       | YES  |     | NULL    |                |
| all_adult_hospital_inpatient_beds_7_day_avg                      | double       | YES  |     | NULL    |                |
| inpatient_beds_used_7_day_avg                                    | double       | YES  |     | NULL    |                |
| all_adult_hospital_inpatient_bed_occupied_7_day_avg              | double       | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_suspected_covid_7d_avg       | double       | YES  |     | NULL    |                |
| total_adult_patients_hospitalized_confirmed_covid_7_day_avg      | double       | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg   | double       | YES  |     | NULL    |                |
| total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg  | double       | YES  |     | NULL    |                |
| inpatient_beds_7_day_avg                                         | double       | YES  |     | NULL    |                |
| total_icu_beds_7_day_avg                                         | double       | YES  |     | NULL    |                |
| total_staffed_adult_icu_beds_7_day_avg                           | double       | YES  |     | NULL    |                |
| icu_beds_used_7_day_avg                                          | double       | YES  |     | NULL    |                |
| staffed_adult_icu_bed_occupancy_7_day_avg                        | double       | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg      | double       | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_covid_7_day_avg             | double       | YES  |     | NULL    |                |
| total_patients_hospitalized_confirmed_influenza_7_day_avg        | double       | YES  |     | NULL    |                |
| icu_patients_confirmed_influenza_7_day_avg                       | double       | YES  |     | NULL    |                |
| total_patients_hosp_confirmed_influenza_and_covid_7d_avg         | double       | YES  |     | NULL    |                |
| total_beds_7_day_sum                                             | int(11)      | YES  |     | NULL    |                |
| all_adult_hospital_beds_7_day_sum                                | int(11)      | YES  |     | NULL    |                |
| all_adult_hospital_inpatient_beds_7_day_sum                      | int(11)      | YES  |     | NULL    |                |
| inpatient_beds_used_7_day_sum                                    | int(11)      | YES  |     | NULL    |                |
| all_adult_hospital_inpatient_bed_occupied_7_day_sum              | int(11)      | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_suspected_covid_7d_sum       | int(11)      | YES  |     | NULL    |                |
| total_adult_patients_hospitalized_confirmed_covid_7_day_sum      | int(11)      | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum   | int(11)      | YES  |     | NULL    |                |
| total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum  | int(11)      | YES  |     | NULL    |                |
| inpatient_beds_7_day_sum                                         | int(11)      | YES  |     | NULL    |                |
| total_icu_beds_7_day_sum                                         | int(11)      | YES  |     | NULL    |                |
| total_staffed_adult_icu_beds_7_day_sum                           | int(11)      | YES  |     | NULL    |                |
| icu_beds_used_7_day_sum                                          | int(11)      | YES  |     | NULL    |                |
| staffed_adult_icu_bed_occupancy_7_day_sum                        | int(11)      | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum      | int(11)      | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_covid_7_day_sum             | int(11)      | YES  |     | NULL    |                |
| total_patients_hospitalized_confirmed_influenza_7_day_sum        | int(11)      | YES  |     | NULL    |                |
| icu_patients_confirmed_influenza_7_day_sum                       | int(11)      | YES  |     | NULL    |                |
| total_patients_hosp_confirmed_influenza_and_covid_7d_sum         | int(11)      | YES  |     | NULL    |                |
| total_beds_7_day_coverage                                        | int(11)      | YES  |     | NULL    |                |
| all_adult_hospital_beds_7_day_coverage                           | int(11)      | YES  |     | NULL    |                |
| all_adult_hospital_inpatient_beds_7_day_coverage                 | int(11)      | YES  |     | NULL    |                |
| inpatient_beds_used_7_day_coverage                               | int(11)      | YES  |     | NULL    |                |
| all_adult_hospital_inpatient_bed_occupied_7_day_coverage         | int(11)      | YES  |     | NULL    |                |
| total_adult_patients_hosp_confirmed_suspected_covid_7d_cov       | int(11)      | YES  |     | NULL    |                |
| total_adult_patients_hospitalized_confirmed_covid_7_day_coverage | int(11)      | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov   | int(11)      | YES  |     | NULL    |                |
| total_pediatric_patients_hosp_confirmed_covid_7d_cov             | int(11)      | YES  |     | NULL    |                |
| inpatient_beds_7_day_coverage                                    | int(11)      | YES  |     | NULL    |                |
| total_icu_beds_7_day_coverage                                    | int(11)      | YES  |     | NULL    |                |
| total_staffed_adult_icu_beds_7_day_coverage                      | int(11)      | YES  |     | NULL    |                |
| icu_beds_used_7_day_coverage                                     | int(11)      | YES  |     | NULL    |                |
| staffed_adult_icu_bed_occupancy_7_day_coverage                   | int(11)      | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov      | int(11)      | YES  |     | NULL    |                |
| staffed_icu_adult_patients_confirmed_covid_7_day_coverage        | int(11)      | YES  |     | NULL    |                |
| total_patients_hospitalized_confirmed_influenza_7_day_coverage   | int(11)      | YES  |     | NULL    |                |
| icu_patients_confirmed_influenza_7_day_coverage                  | int(11)      | YES  |     | NULL    |                |
| total_patients_hosp_confirmed_influenza_and_covid_7d_cov         | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_7_day_sum           | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_18_19_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_20_29_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_30_39_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_40_49_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_50_59_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_60_69_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_70_79_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_80plus_7_day_sum    | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_confirmed_unknown_7_day_sum   | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_pediatric_covid_confirmed_7_day_sum       | int(11)      | YES  |     | NULL    |                |
| previous_day_covid_ed_visits_7_day_sum                           | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_7_day_sum           | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_18_19_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_20_29_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_30_39_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_40_49_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_50_59_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_60_69_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_70_79_7_day_sum     | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_80plus_7_day_sum    | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_adult_covid_suspected_unknown_7_day_sum   | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_pediatric_covid_suspected_7_day_sum       | int(11)      | YES  |     | NULL    |                |
| previous_day_total_ed_visits_7_day_sum                           | int(11)      | YES  |     | NULL    |                |
| previous_day_admission_influenza_confirmed_7_day_sum             | int(11)      | YES  |     | NULL    |                |
+------------------------------------------------------------------+--------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `publication_date`
  the day (YYYYMMDD) that the dataset was published. equivalent to `issue` in
  the state timeseries and metadata tables, but renamed here for clarity.

NOTE: `collection_week` is the first day (YYYYMMDD) of the week to which the
data applies. this is a weekly rollup of daily data from friday to thursday. as
a result, we can't use sunday-to-saturday epiweeks (YYYYMM) to identify the
week, so we instead use the date of friday, as is done in the upstream data
source.

NOTE: Names have been shortened to 64 characters, as this is a technical
limitation of the database. Affected names are:

total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg ->
  total_adult_patients_hosp_confirmed_suspected_covid_7d_avg
total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg ->
  total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg
staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_avg ->
  staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg
total_patients_hospitalized_confirmed_influenza_and_covid_7_day_avg ->
  total_patients_hosp_confirmed_influenza_and_covid_7d_avg
total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_sum ->
  total_adult_patients_hosp_confirmed_suspected_covid_7d_sum
total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_sum ->
  total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum
staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_sum ->
  staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum
total_patients_hospitalized_confirmed_influenza_and_covid_7_day_sum ->
  total_patients_hosp_confirmed_influenza_and_covid_7d_sum
total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage ->
  total_adult_patients_hosp_confirmed_suspected_covid_7d_cov
total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage ->
  total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov
total_pediatric_patients_hospitalized_confirmed_covid_7_day_coverage ->
  total_pediatric_patients_hosp_confirmed_covid_7d_cov
staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_coverage ->
  staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov
total_patients_hospitalized_confirmed_influenza_and_covid_7_day_coverage ->
  total_patients_hosp_confirmed_influenza_and_covid_7d_cov

NOTE: Names have been normalized according to the following rules:
- replace `-` with `_` (e.g. "70-79" -> "70_79")
- replace `+` with `plus` (e.g. "80+" -> "80plus")
- convert to lowercase (e.g. "ED" -> "ed")

NOTE: the following data dictionary is copied from
https://healthdata.gov/covid-19-reported-patient-impact-and-hospital-capacity-facility-data-dictionary
version entitled "Wed, 12/09/2020 - 17:23".

- `hospital_pk`
  This unique key for the given hospital that will match the ccn column if it
  exists, otherwise, it is a derived unique key.
- `collection_week`
  This date indicates the start of the period of reporting (the starting
  Friday).
- `state`
  [FAQ - 1. d)] The two digit state/territory code for the hospital.
- `ccn`
  [FAQ - 1. b)] CMS Certification Number (CCN) of the given facility
- `hospital_name`
  [FAQ - 1. a)] The name of the facility reporting.
- `address`
  The address of the facility reporting.
- `city`
  The city of the facility reporting.
- `zip`
  The 5-digit zip code of the facility reporting.
- `hospital_subtype`
  The sub-type of the facility reporting. Valid values are: Children's
  Hospitals, Critical Access Hospitals, Long Term, Psychiatric, Rehabilitation
  & Short Term. Some facilities are not designated with this field.
- `fips_code`
  The Federal Information Processing Standard (FIPS) code of the location of
  the hospital.
- `is_metro_micro`
  This is based on whether the facility serves a Metropolitan or Micropolitan
  area. True if yes, and false if no.
- `total_beds_7_day_avg`
  [FAQ - 2. a)] Average of total number of all staffed inpatient and outpatient
  beds in the hospital, including all overflow, observation, and active
  surge/expansion beds used for inpatients and for outpatients (including all
  ICU, ED, and observation) reported during the 7-day period.
- `all_adult_hospital_beds_7_day_avg`
  [FAQ - 2. b)] Average of all staffed inpatient and outpatient adult beds in
  the hospital, including all overflow and active surge/expansion beds for
  inpatients and for outpatients (including all ICU, ED, and observation)
  reported during the 7-day period.
- `all_adult_hospital_inpatient_beds_7_day_avg`
  [FAQ - 3. b)] Average of total number of staffed inpatient adult beds in the
  hospital including all overflow and active surge/expansion beds used for
  inpatients (including all designated ICU beds) reported during the 7-day
  period.
- `inpatient_beds_used_7_day_avg`
  [FAQ - 4. a)] Average of total number of staffed inpatient beds that are
  occupied reported during the 7-day period.
- `all_adult_hospital_inpatient_bed_occupied_7_day_avg`
  [FAQ - 4. b)] Average of total number of staffed inpatient adult beds that
  are occupied reported during the 7-day period.
- `total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg`
  [FAQ - 9. a)] Average number of patients currently hospitalized in an adult
  inpatient bed who have laboratory-confirmed or suspected COVID19, including
  those in observation beds reported during the 7-day period.
- `total_adult_patients_hospitalized_confirmed_covid_7_day_avg`
  [FAQ - 9. b)] Average number of patients currently hospitalized in an adult
  inpatient bed who have laboratory-confirmed COVID-19, including those in
  observation beds. This average includes patients who have both
  laboratory-confirmed COVID-19 and laboratory-confirmed influenza.
- `total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg`
  [FAQ - 10. a)] Average number of patients currently hospitalized in a
  pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who are
  suspected or laboratory-confirmed-positive for COVID-19. This average
  includes those in observation beds reported in the 7-day period.
- `total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg`
  [FAQ - 10. b)] Average number of patients currently hospitalized in a
  pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who have
  laboratory-confirmed COVID-19. Including those in observation beds. Including
  patients who have both laboratory-confirmed COVID-19 and laboratory confirmed
  influenza in this field reported in the 7-day period.
- `inpatient_beds_7_day_avg`
  [FAQ - 3. a)] Average number of total number of staffed inpatient beds in
  your hospital including all overflow, observation, and active surge/expansion
  beds used for inpatients (including all ICU beds) reported in the 7-day
  period.
- `total_icu_beds_7_day_avg`
  [FAQ - 5. a)] Average of total number of staffed inpatient ICU beds reported
  in the 7-day period.
- `total_staffed_adult_icu_beds_7_day_avg`
  [FAQ - 5. b)] Average number of total number of staffed inpatient ICU beds
  reported in the 7-day period.
- `icu_beds_used_7_day_avg`
  [FAQ - 6. a)] Average number of total number of staffed inpatient ICU beds
  reported in the 7-day period.
- `staffed_adult_icu_bed_occupancy_7_day_avg`
  [FAQ - 6. b)] Average of total number of staffed inpatient adult ICU beds
  that are occupied reported in the 7-day period.
- `staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_avg`
  [FAQ - 12. a)] Average number of patients currently hospitalized in a
  designated adult ICU bed who have suspected or laboratory-confirmed COVID-19
  reported in the 7-day period.
- `staffed_icu_adult_patients_confirmed_covid_7_day_avg`
  [FAQ - 12. b)] Average number of patients currently hospitalized in a
  designated adult ICU bed who have laboratory-confirmed COVID-19. Including
  patients who have both laboratory-confirmed COVID-19 and laboratory-confirmed
  influenza in this field reported in the 7-day period.
- `total_patients_hospitalized_confirmed_influenza_7_day_avg`
  [FAQ - 33] Average number of patients (all ages) currently hospitalized in an
  inpatient bed who have laboratory-confirmed influenza. Including those in
  observation beds reported in the 7-day period.
- `icu_patients_confirmed_influenza_7_day_avg`
  [FAQ - 35] Average of patients (all ages) currently hospitalized in a
  designated ICU bed with laboratory-confirmed influenza in the 7-day period.
- `total_patients_hospitalized_confirmed_influenza_and_covid_7_day_avg`
  [FAQ - 36] Average number of patients (all ages) currently hospitalized in an
  inpatient bed who have laboratory-confirmed COVID-19 and laboratory-confirmed
  influenza reported in the 7-day period.
- `total_beds_7_day_sum`
  [FAQ - 2. a)] Sum of reports of total number of all staffed inpatient and
  outpatient beds in the hospital, including all overflow, observation, and
  active surge/expansion beds used for inpatients and for outpatients
  (including all ICU, ED, and observation) reported during the 7-day period.
- `all_adult_hospital_beds_7_day_sum`
  [FAQ - 2. b)] Sum of reports of all staffed inpatient and outpatient adult
  beds in the hospital, including all overflow and active surge/expansion beds
  for inpatients and for outpatients (including all ICU, ED, and observation)
  reported during the 7-day period.
- `all_adult_hospital_inpatient_beds_7_day_sum`
  [FAQ - 3. b)] Sum of reports of all staffed inpatient and outpatient adult
  beds in the hospital, including all overflow and active surge/expansion beds
  for inpatients and for outpatients (including all ICU, ED, and observation)
  reported during the 7-day period.
- `inpatient_beds_used_7_day_sum`
  [FAQ - 4. a)] Sum of reports of total number of staffed inpatient beds that
  are occupied reported during the 7-day period.
- `all_adult_hospital_inpatient_bed_occupied_7_day_sum`
  [FAQ - 4. b)] Sum of reports of total number of staffed inpatient adult beds
  that are occupied reported during the 7-day period.
- `total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_sum`
  [FAQ - 9. a)] Sum of reports of patients currently hospitalized in an adult
  inpatient bed who have laboratory-confirmed or suspected COVID19. Including
  those in observation beds reported during the 7-day period.
- `total_adult_patients_hospitalized_confirmed_covid_7_day_sum`
  [FAQ - 9. b)] Sum of reports of patients currently hospitalized in an adult
  inpatient bed who have laboratory-confirmed COVID-19. Including those in
  observation beds. Including patients who have both laboratory-confirmed
  COVID-19 and laboratory confirmed influenza in this field during the 7-day
  period.
- `total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_sum`
  [FAQ - 10. a)] Sum of reports of patients currently hospitalized in a
  pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who are
  suspected or laboratory-confirmed-positive for COVID-19. Including those in
  observation beds reported in the 7-day period.
- `total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum`
  [FAQ - 10. b)] Sum of reports of patients currently hospitalized in a
  pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who have
  laboratory-confirmed COVID-19. Including those in observation beds. Including
  patients who have both laboratory-confirmed COVID-19 and laboratory confirmed
  influenza in this field reported in the 7-day period.
- `inpatient_beds_7_day_sum`
  [FAQ - 3. a)] Sum of reports of total number of staffed inpatient beds in
  your hospital including all overflow, observation, and active surge/expansion
  beds used for inpatients (including all ICU beds) reported in the 7-day
  period.
- `total_icu_beds_7_day_sum`
  [FAQ - 5. a)] Sum of reports of total number of staffed inpatient ICU beds
  reported in the 7-day period.
- `total_staffed_adult_icu_beds_7_day_sum`
  [FAQ - 5. b)] Sum of reports of total number of staffed inpatient adult ICU
  beds reported in the 7-day period.
- `icu_beds_used_7_day_sum`
  [FAQ - 5. b)] Sum of reports of total number of staffed inpatient ICU beds
  reported in the 7-day period.
- `staffed_adult_icu_bed_occupancy_7_day_sum`
  [FAQ - 6. b)] Sum of reports of total number of staffed inpatient adult ICU
  beds that are occupied reported in the 7-day period.
- `staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_sum`
  [FAQ - 12. a)] Sum of reports of patients currently hospitalized in a
  designated adult ICU bed who have suspected or laboratory-confirmed COVID-19
  reported in the 7-day period.
- `staffed_icu_adult_patients_confirmed_covid_7_day_sum`
  [FAQ - 12. b)] Sum of reports of patients currently hospitalized in a
  designated adult ICU bed who have laboratory-confirmed COVID-19. Including
  patients who have both laboratory-confirmed COVID-19 and laboratory-confirmed
  influenza in this field reported in the 7-day period.
- `total_patients_hospitalized_confirmed_influenza_7_day_sum`
  [FAQ - 33] Sum of reports of patients (all ages) currently hospitalized in an
  inpatient bed who have laboratory-confirmed influenza. Including those in
  observation beds reported in the 7-day period.
- `icu_patients_confirmed_influenza_7_day_sum`
  [FAQ - 35] Sum of reports of patients (all ages) currently hospitalized in a
  designated ICU bed with laboratory-confirmed influenza reported in the 7-day
  period.
- `total_patients_hospitalized_confirmed_influenza_and_covid_7_day_sum`
  [FAQ - 36] Sum of reports of patients (all ages) currently hospitalized in an
  inpatient bed who have laboratory-confirmed COVID-19 and laboratory-confirmed
  influenza reported in the 7-day period.
- `total_beds_7_day_coverage`
  [FAQ - 2. a)] Number of times in the 7 day period that the facility reported
  total number of all staffed inpatient and outpatient beds in your hospital,
  including all overflow, observation, and active surge/expansion beds used for
  inpatients and for outpatients (including all ICU, ED, and observation).
- `all_adult_hospital_beds_7_day_coverage`
  [FAQ - 2. b)] Number of times in the 7-day period that the facility reported
  total number of all staffed inpatient and outpatient adult beds in your
  hospital, including all overflow and active surge/expansion beds for
  inpatients and for outpatients (including all ICU, ED, and observation).
- `all_adult_hospital_inpatient_beds_7_day_coverage`
  [FAQ - 3. b)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient adult beds in your hospital including all
  overflow and active surge/expansion beds used for inpatients (including all
  designated ICU beds).
- `inpatient_beds_used_7_day_coverage`
  [FAQ - 4. a)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient beds that are occupied.
- `all_adult_hospital_inpatient_bed_occupied_7_day_coverage`
  [FAQ - 4. b)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient adult beds that are occupied.
- `total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage`
  [FAQ - 9. a)] Number of times in the 7-day period that the facility reported
  patients currently hospitalized in an adult inpatient bed who have
  laboratory-confirmed or suspected COVID19. Including those in observation
  beds.
- `total_adult_patients_hospitalized_confirmed_covid_7_day_coverage`
  [FAQ - 9. b)] Number of times in the 7-day period that the facility reported
  patients currently hospitalized in an adult inpatient bed who have
  laboratory-confirmed COVID-19. Including those in observation beds. Including
  patients who have both laboratory-confirmed COVID-19 and laboratory confirmed
  influenza in this field.
- `total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage`
  [FAQ - 10. a)] Number of times in the 7-day period that the facility reported
  Patients currently hospitalized in a pediatric inpatient bed, including NICU,
  PICU, newborn, and nursery, who are suspected or
  laboratory-confirmed-positive for COVID-19. Including those in observation
  beds.
- `total_pediatric_patients_hospitalized_confirmed_covid_7_day_coverage`
  [FAQ - 10. b)] Number of times in the 7-day period that the facility reported
  patients currently hospitalized in a pediatric inpatient bed, including NICU,
  PICU, newborn, and nursery, who have laboratory-confirmed COVID-19. Including
  those in observation beds. Including patients who have both
  laboratory-confirmed COVID-19 and laboratory confirmed influenza in this
  field.
- `inpatient_beds_7_day_coverage`
  [FAQ - 3. a)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient beds in your hospital including all
  overflow, observation, and active surge/expansion beds used for inpatients
  (including all ICU beds).
- `total_icu_beds_7_day_coverage`
  [FAQ - 5. a)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient ICU beds.
- `total_staffed_adult_icu_beds_7_day_coverage`
  [FAQ - 5. b)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient adult ICU beds.
- `icu_beds_used_7_day_coverage`
  [FAQ - 6. a)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient ICU beds.
- `staffed_adult_icu_bed_occupancy_7_day_coverage`
  [FAQ - 6. b)] Number of times in the 7-day period that the facility reported
  total number of staffed inpatient adult ICU beds that are occupied.
- `staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_coverage`
  [FAQ - 12. a)] Number of times in the 7-day period that the facility reported
  patients currently hospitalized in a designated adult ICU bed who have
  suspected or laboratory-confirmed COVID-19.
- `staffed_icu_adult_patients_confirmed_covid_7_day_coverage`
  [FAQ - 12. b)] Number of times in the 7-day period that the facility reported
  patients currently hospitalized in a designated adult ICU bed who have
  laboratory-confirmed COVID-19. Including patients who have both
  laboratory-confirmed COVID-19 and laboratory-confirmed influenza in this
  field.
- `total_patients_hospitalized_confirmed_influenza_7_day_coverage`
  [FAQ - 33] Number of times in the 7-day period that the facility reported
  patients (all ages) currently hospitalized in an inpatient bed who have
  laboratory-confirmed influenza. Including those in observation beds.
- `icu_patients_confirmed_influenza_7_day_coverage`
  [FAQ - 35] Number of times in the 7-day period that the facility reported
  patients (all ages) currently hospitalized in a designated ICU bed with
  laboratory-confirmed influenza.
- `total_patients_hospitalized_confirmed_influenza_and_covid_7_day_coverage`
  [FAQ - 36] Number of times in the 7-day period that the facility reported
  patients (all ages) currently hospitalized in an inpatient bed who have
  laboratory-confirmed COVID-19 and laboratory-confirmed influenza.
- `previous_day_admission_adult_covid_confirmed_7_day_sum`
  [FAQ - 17. a)] Sum of number of patients who were admitted to an adult
  inpatient bed on the previous calendar day who had confirmed COVID-19 at the
  time of admission reported in the 7-day period.
- `previous_day_admission_adult_covid_confirmed_18-19_7_day_sum`
  [FAQ - 17. a1)] Sum of number of patients age 18-19 who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in the 7-day period.
- `previous_day_admission_adult_covid_confirmed_20-29_7_day_sum`
  [FAQ - 17. a2)] Sum of number of patients age 20-29 who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in the 7-day period.
- `previous_day_admission_adult_covid_confirmed_30-39_7_day_sum`
  [FAQ - 17. a3)] Sum of number of patients age 30-39 who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_confirmed_40-49_7_day_sum`
  [FAQ - 17. a4)] Sum of number of patients age 40-49 who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_confirmed_50-59_7_day_sum`
  [FAQ - 17. a5)] Sum of number of patients age 50-59 who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_confirmed_60-69_7_day_sum`
  [FAQ - 17. a6)] Sum of number of patients age 60-69 who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_confirmed_70-79_7_day_sum`
  [FAQ - 17. a7)] Sum of number of patients age 70-79 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_confirmed_80+_7_day_sum`
  [FAQ - 17. a8)] Sum of number of patients 80 or older who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_confirmed_unknown_7_day_sum`
  [FAQ - 17. a9)] Sum of number of patients age unknown who were admitted to an
  adult inpatient bed on the previous calendar day who had confirmed COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_pediatric_covid_confirmed_7_day_sum`
  [FAQ - 18. a)] Sum of number of pediatric patients who were admitted to an
  inpatient bed, including NICU, PICU, newborn, and nursery, on the previous
  calendar day who had confirmed COVID-19 at the time of admission.
- `previous_day_covid_ED_visits_7_day_sum`
  [FAQ - 20] Sum of total number of ED visits who were seen on the previous
  calendar day who had a visit related to COVID-19 (meets suspected or
  confirmed definition or presents for COVID diagnostic testing – do not count
  patients who present for pre-procedure screening) reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_7_day_sum`
  [FAQ - 17. b)] Sum of number of patients who were admitted to an adult
  inpatient bed on the previous calendar day who had suspected COVID-19 at the
  time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_18-19_7_day_sum`
  [FAQ - 17. b1)] Sum of number of patients age 18-19 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_20-29_7_day_sum`
  [FAQ - 17. b2)] Sum of number of patients age 20-29 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_30-39_7_day_sum`
  [FAQ - 17. b3)] Sum of number of patients age 30-39 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_40-49_7_day_sum`
  [FAQ - 17. b4)] Sum of number of patients age 40-49 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_50-59_7_day_sum`
  [FAQ - 17. b5)] Sum of number of patients age 50-59 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_60-69_7_day_sum`
  [FAQ - 17. b6)] Sum of number of patients age 60-69 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_70-79_7_day_sum`
  [FAQ - 17. b7)] Sum of number of patients age 70-79 who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_80+_7_day_sum`
  [FAQ - 17. b8)] Sum of number of patients 80 or older who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_adult_covid_suspected_unknown_7_day_sum`
  [FAQ - 17. b9)] Sum of number of patients age unknown who were admitted to an
  adult inpatient bed on the previous calendar day who had suspected COVID-19
  at the time of admission reported in 7-day period.
- `previous_day_admission_pediatric_covid_suspected_7_day_sum`
  [FAQ - 18. b)] Sum of number of pediatrics patients who were admitted to an
  inpatient bed, including NICU, PICU, newborn, and nursery, on the previous
  calendar day who had suspected COVID-19 at the time of admission reported in
  7-day period.
- `previous_day_total_ED_visits_7_day_sum`
  [FAQ - 19] Sum of total number of patient visits to the ED who were seen on
  the previous calendar day regardless of reason for visit. Including all
  patients who are triaged even if they leave before being seen by a provider
  reported in the 7-day period.
- `previous_day_admission_influenza_confirmed_7_day_sum`
  [FAQ - 34] Sum of number of patients (all ages) who were admitted to an
  inpatient bed on the previous calendar day who had laboratory-confirmed
  influenza at the time of admission reported in 7-day period.
*/

CREATE TABLE `covid_hosp_facility` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `publication_date` INT NOT NULL,
  `address` VARCHAR(128),
  `ccn` VARCHAR(20),
  `city` VARCHAR(64),
  `collection_week` INT NOT NULL,
  `fips_code` CHAR(5),
  `geocoded_hospital_address` VARCHAR(32),
  `hhs_ids` VARCHAR(127),
  `hospital_name` VARCHAR(256),
  `hospital_pk` VARCHAR(128) NOT NULL,
  `hospital_subtype` VARCHAR(64),
  `is_metro_micro` BOOLEAN,
  `state` CHAR(2) NOT NULL,
  `zip` CHAR(5),
  -- the below have been relisted in alphabetical order for easier management
  `all_adult_hospital_beds_7_day_avg` DOUBLE,
  `all_adult_hospital_beds_7_day_coverage` INT,
  `all_adult_hospital_beds_7_day_sum` INT,
  `all_adult_hospital_inpatient_bed_occupied_7_day_avg` DOUBLE,
  `all_adult_hospital_inpatient_bed_occupied_7_day_coverage` INT,
  `all_adult_hospital_inpatient_bed_occupied_7_day_sum` INT,
  `all_adult_hospital_inpatient_beds_7_day_avg` DOUBLE,
  `all_adult_hospital_inpatient_beds_7_day_coverage` INT,
  `all_adult_hospital_inpatient_beds_7_day_sum` INT,
  `icu_beds_used_7_day_avg` DOUBLE,
  `icu_beds_used_7_day_coverage` INT,
  `icu_beds_used_7_day_sum` INT,
  `icu_patients_confirmed_influenza_7_day_avg` DOUBLE,
  `icu_patients_confirmed_influenza_7_day_coverage` INT,
  `icu_patients_confirmed_influenza_7_day_sum` INT,
  `inpatient_beds_7_day_avg` DOUBLE,
  `inpatient_beds_7_day_coverage` INT,
  `inpatient_beds_7_day_sum` INT,
  `inpatient_beds_used_7_day_avg` DOUBLE,
  `inpatient_beds_used_7_day_coverage` INT,
  `inpatient_beds_used_7_day_sum` INT,
  `is_corrected` BOOLEAN,
  `previous_day_admission_adult_covid_confirmed_18_19_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_20_29_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_30_39_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_40_49_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_50_59_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_60_69_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_70_79_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_7_day_coverage` INT,
  `previous_day_admission_adult_covid_confirmed_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_80plus_7_day_sum` INT,
  `previous_day_admission_adult_covid_confirmed_unknown_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_18_19_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_20_29_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_30_39_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_40_49_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_50_59_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_60_69_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_70_79_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_7_day_coverage` INT,
  `previous_day_admission_adult_covid_suspected_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_80plus_7_day_sum` INT,
  `previous_day_admission_adult_covid_suspected_unknown_7_day_sum` INT,
  `previous_day_admission_influenza_confirmed_7_day_sum` INT,
  `previous_day_admission_pediatric_covid_confirmed_7_day_coverage` INT,
  `previous_day_admission_pediatric_covid_confirmed_7_day_sum` INT,
  `previous_day_admission_pediatric_covid_suspected_7_day_coverage` INT,
  `previous_day_admission_pediatric_covid_suspected_7_day_sum` INT,
  `previous_day_covid_ed_visits_7_day_sum` INT,
  `previous_day_total_ed_visits_7_day_sum` INT,
  `previous_week_patients_covid_vaccinated_doses_all_7_day_sum` INT,
  `previous_week_patients_covid_vaccinated_doses_all_7_day` INT,
  `previous_week_patients_covid_vaccinated_doses_one_7_day_sum` INT,
  `previous_week_patients_covid_vaccinated_doses_one_7_day` INT,
  `previous_week_personnel_covid_vaccd_doses_administered_7_day_sum` INT,
  `previous_week_personnel_covid_vaccd_doses_administered_7_day` INT,
  `staffed_adult_icu_bed_occupancy_7_day_avg` DOUBLE,
  `staffed_adult_icu_bed_occupancy_7_day_coverage` INT,
  `staffed_adult_icu_bed_occupancy_7_day_sum` INT,
  `staffed_icu_adult_patients_confirmed_covid_7_day_avg` DOUBLE,
  `staffed_icu_adult_patients_confirmed_covid_7_day_coverage` INT,
  `staffed_icu_adult_patients_confirmed_covid_7_day_sum` INT,
  `staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg` DOUBLE,
  `staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov` INT,
  `staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum` INT,
  `total_adult_patients_hosp_confirmed_suspected_covid_7d_avg` DOUBLE,
  `total_adult_patients_hosp_confirmed_suspected_covid_7d_cov` INT,
  `total_adult_patients_hosp_confirmed_suspected_covid_7d_sum` INT,
  `total_adult_patients_hospitalized_confirmed_covid_7_day_avg` DOUBLE,
  `total_adult_patients_hospitalized_confirmed_covid_7_day_coverage` INT,
  `total_adult_patients_hospitalized_confirmed_covid_7_day_sum` INT,
  `total_beds_7_day_avg` DOUBLE,
  `total_beds_7_day_coverage` INT,
  `total_beds_7_day_sum` INT,
  `total_icu_beds_7_day_avg` DOUBLE,
  `total_icu_beds_7_day_coverage` INT,
  `total_icu_beds_7_day_sum` INT,
  `total_patients_hosp_confirmed_influenza_and_covid_7d_avg` DOUBLE,
  `total_patients_hosp_confirmed_influenza_and_covid_7d_cov` INT,
  `total_patients_hosp_confirmed_influenza_and_covid_7d_sum` INT,
  `total_patients_hospitalized_confirmed_influenza_7_day_avg` DOUBLE,
  `total_patients_hospitalized_confirmed_influenza_7_day_coverage` INT,
  `total_patients_hospitalized_confirmed_influenza_7_day_sum` INT,
  `total_pediatric_patients_hosp_confirmed_covid_7d_cov` INT,
  `total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg` DOUBLE,
  `total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov` INT,
  `total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum` INT,
  `total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg` DOUBLE,
  `total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum` INT,
  `total_personnel_covid_vaccinated_doses_all_7_day_sum` INT,
  `total_personnel_covid_vaccinated_doses_all_7_day` INT,
  `total_personnel_covid_vaccinated_doses_none_7_day_sum` INT,
  `total_personnel_covid_vaccinated_doses_none_7_day` INT,
  `total_personnel_covid_vaccinated_doses_one_7_day_sum` INT,
  `total_personnel_covid_vaccinated_doses_one_7_day` INT,
  `total_staffed_adult_icu_beds_7_day_avg` DOUBLE,
  `total_staffed_adult_icu_beds_7_day_coverage` INT,
  `total_staffed_adult_icu_beds_7_day_sum` INT,
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of most recent publication date for a given hospital and week
  UNIQUE KEY (`hospital_pk`, `collection_week`, `publication_date`),
  -- for fast lookup of a time-series for a given hospital and publication date
  KEY (`publication_date`, `hospital_pk`, `collection_week`),
  -- for fast lookup of hospitals in a given location
  KEY (`state`, `hospital_pk`),
  KEY (`ccn`, `hospital_pk`),
  KEY (`city`, `hospital_pk`),
  KEY (`zip`, `hospital_pk`),
  KEY (`fips_code`, `hospital_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
