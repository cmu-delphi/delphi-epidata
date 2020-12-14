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
| revision_timestamp   | varchar(1024) | NO   |     | NULL    |                |
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
  `revision_timestamp` VARCHAR(1024) NOT NULL,
  `metadata_json` JSON NOT NULL,
  `acquisition_datetime` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of a particular revision for a specific dataset
  UNIQUE KEY (`dataset_name`, `revision_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*
`covid_hosp_state_timeseries` stores the versioned "state timeseries" dataset.

Data is public under the Open Data Commons Open Database License (ODbL).

+------------------------------------------------------------------+---------+------+-----+---------+----------------+
| Field                                                            | Type    | Null | Key | Default | Extra          |
+------------------------------------------------------------------+---------+------+-----+---------+----------------+
| id                                                               | int(11) | NO   | PRI | NULL    | auto_increment |
| issue                                                            | int(11) | NO   | MUL | NULL    |                |
| state                                                            | char(2) | NO   | MUL | NULL    |                |
| date                                                             | int(11) | NO   |     | NULL    |                |
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
version entitled "November 16, 2020 release 2.3".

- `state`
  The two digit state code
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

NOTE: the following field is defined in the data dictionary but does not
actually appear in the dataset.

- `reporting_cutoff_start`
  Look back date start - The latest reports from each hospital is summed for
  this report starting with this date.
*/

CREATE TABLE `covid_hosp_state_timeseries` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `issue` INT NOT NULL,
  `state` CHAR(2) NOT NULL,
  `date` INT NOT NULL,
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
  PRIMARY KEY (`id`),
  -- for uniqueness
  -- for fast lookup of most recent issue for a given state and date
  UNIQUE KEY `issue_by_state_and_date` (`state`, `date`, `issue`),
  -- for fast lookup of a time-series for a given state and issue
  KEY `date_by_issue_and_state` (`issue`, `state`, `date`),
  -- for fast lookup of all states for a given date and issue
  KEY `state_by_issue_and_date` (`issue`, `date`, `state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
