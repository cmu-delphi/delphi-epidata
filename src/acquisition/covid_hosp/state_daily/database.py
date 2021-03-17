# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils

import pandas as pd


class Database(BaseDatabase):

  # note we share a database with state_timeseries
  TABLE_NAME = 'covid_hosp_state_timeseries'
  CSV_DATE_COL = 'reporting_cutoff_start'
  # These are 3-tuples of (CSV header name, SQL db column name, data type) for
  # all the columns in the CSV file.
  # Note that the corresponding database column names may be shorter
  # due to constraints on the length of column names. See
  # /src/ddl/covid_hosp.sql for more information.
  # Additionally, all column names below are shared with state_timeseries,
  # except for reporting_cutoff_start (here) and date (there). If you need
  # to update a column name, do it in both places.
  ORDERED_CSV_COLUMNS = [
    ('state', 'state', str),
    (CSV_DATE_COL, 'date', Utils.int_from_date),
    ('critical_staffing_shortage_today_yes', 'critical_staffing_shortage_today_yes', int),
    ('critical_staffing_shortage_today_no', 'critical_staffing_shortage_today_no', int),
    ('critical_staffing_shortage_today_not_reported',
     'critical_staffing_shortage_today_not_reported', int),
    ('critical_staffing_shortage_anticipated_within_week_yes',
     'critical_staffing_shortage_anticipated_within_week_yes', int),
    ('critical_staffing_shortage_anticipated_within_week_no',
     'critical_staffing_shortage_anticipated_within_week_no', int),
    ('critical_staffing_shortage_anticipated_within_week_not_reported',
     'critical_staffing_shortage_anticipated_within_week_not_reported', int),
    ('hospital_onset_covid', 'hospital_onset_covid', int),
    ('hospital_onset_covid_coverage', 'hospital_onset_covid_coverage', int),
    ('inpatient_beds', 'inpatient_beds', int),
    ('inpatient_beds_coverage', 'inpatient_beds_coverage', int),
    ('inpatient_beds_used', 'inpatient_beds_used', int),
    ('inpatient_beds_used_coverage', 'inpatient_beds_used_coverage', int),
    ('inpatient_beds_used_covid', 'inpatient_beds_used_covid', int),
    ('inpatient_beds_used_covid_coverage', 'inpatient_beds_used_covid_coverage', int),
    ('previous_day_admission_adult_covid_confirmed', 'previous_day_admission_adult_covid_confirmed',
     int),
    ('previous_day_admission_adult_covid_confirmed_coverage',
     'previous_day_admission_adult_covid_confirmed_coverage', int),
    ('previous_day_admission_adult_covid_suspected', 'previous_day_admission_adult_covid_suspected',
     int),
    ('previous_day_admission_adult_covid_suspected_coverage',
     'previous_day_admission_adult_covid_suspected_coverage', int),
    ('previous_day_admission_pediatric_covid_confirmed',
     'previous_day_admission_pediatric_covid_confirmed', int),
    ('previous_day_admission_pediatric_covid_confirmed_coverage',
     'previous_day_admission_pediatric_covid_confirmed_coverage', int),
    ('previous_day_admission_pediatric_covid_suspected',
     'previous_day_admission_pediatric_covid_suspected', int),
    ('previous_day_admission_pediatric_covid_suspected_coverage',
     'previous_day_admission_pediatric_covid_suspected_coverage', int),
    ('staffed_adult_icu_bed_occupancy', 'staffed_adult_icu_bed_occupancy', int),
    ('staffed_adult_icu_bed_occupancy_coverage', 'staffed_adult_icu_bed_occupancy_coverage', int),
    ('staffed_icu_adult_patients_confirmed_and_suspected_covid',
     'staffed_icu_adult_patients_confirmed_suspected_covid', int),
    ('staffed_icu_adult_patients_confirmed_and_suspected_covid_coverage',
     'staffed_icu_adult_patients_confirmed_suspected_covid_coverage', int),
    ('staffed_icu_adult_patients_confirmed_covid', 'staffed_icu_adult_patients_confirmed_covid',
     int),
    ('staffed_icu_adult_patients_confirmed_covid_coverage',
     'staffed_icu_adult_patients_confirmed_covid_coverage', int),
    ('total_adult_patients_hospitalized_confirmed_and_suspected_covid',
     'total_adult_patients_hosp_confirmed_suspected_covid', int),
    ('total_adult_patients_hospitalized_confirmed_and_suspected_covid_coverage',
     'total_adult_patients_hosp_confirmed_suspected_covid_coverage', int),
    ('total_adult_patients_hospitalized_confirmed_covid',
     'total_adult_patients_hosp_confirmed_covid', int),
    ('total_adult_patients_hospitalized_confirmed_covid_coverage',
     'total_adult_patients_hosp_confirmed_covid_coverage', int),
    ('total_pediatric_patients_hospitalized_confirmed_and_suspected_covid',
     'total_pediatric_patients_hosp_confirmed_suspected_covid', int),
    ('total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_coverage',
     'total_pediatric_patients_hosp_confirmed_suspected_covid_coverage', int),
    ('total_pediatric_patients_hospitalized_confirmed_covid',
     'total_pediatric_patients_hosp_confirmed_covid', int),
    ('total_pediatric_patients_hospitalized_confirmed_covid_coverage',
     'total_pediatric_patients_hosp_confirmed_covid_coverage', int),
    ('total_staffed_adult_icu_beds', 'total_staffed_adult_icu_beds', int),
    ('total_staffed_adult_icu_beds_coverage', 'total_staffed_adult_icu_beds_coverage', int),
    ('inpatient_beds_utilization', 'inpatient_beds_utilization', float),
    ('inpatient_beds_utilization_coverage', 'inpatient_beds_utilization_coverage', int),
    ('inpatient_beds_utilization_numerator', 'inpatient_beds_utilization_numerator', int),
    ('inpatient_beds_utilization_denominator', 'inpatient_beds_utilization_denominator', int),
    ('percent_of_inpatients_with_covid', 'percent_of_inpatients_with_covid', float),
    ('percent_of_inpatients_with_covid_coverage', 'percent_of_inpatients_with_covid_coverage', int),
    ('percent_of_inpatients_with_covid_numerator', 'percent_of_inpatients_with_covid_numerator',
     int),
    ('percent_of_inpatients_with_covid_denominator', 'percent_of_inpatients_with_covid_denominator',
     int),
    ('inpatient_bed_covid_utilization', 'inpatient_bed_covid_utilization', float),
    ('inpatient_bed_covid_utilization_coverage', 'inpatient_bed_covid_utilization_coverage', int),
    ('inpatient_bed_covid_utilization_numerator', 'inpatient_bed_covid_utilization_numerator', int),
    ('inpatient_bed_covid_utilization_denominator', 'inpatient_bed_covid_utilization_denominator',
     int),
    ('adult_icu_bed_covid_utilization', 'adult_icu_bed_covid_utilization', float),
    ('adult_icu_bed_covid_utilization_coverage', 'adult_icu_bed_covid_utilization_coverage', int),
    ('adult_icu_bed_covid_utilization_numerator', 'adult_icu_bed_covid_utilization_numerator', int),
    ('adult_icu_bed_covid_utilization_denominator', 'adult_icu_bed_covid_utilization_denominator',
     int),
    ('adult_icu_bed_utilization', 'adult_icu_bed_utilization', float),
    ('adult_icu_bed_utilization_coverage', 'adult_icu_bed_utilization_coverage', int),
    ('adult_icu_bed_utilization_numerator', 'adult_icu_bed_utilization_numerator', int),
    ('adult_icu_bed_utilization_denominator', 'adult_icu_bed_utilization_denominator', int),
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(
        *args,
        **kwargs,
        table_name=Database.TABLE_NAME,
        columns_and_types=Database.ORDERED_CSV_COLUMNS,
        additional_fields=[('D', 'record_type')])
