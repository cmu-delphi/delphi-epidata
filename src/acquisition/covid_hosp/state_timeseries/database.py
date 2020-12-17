# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils


class Database(BaseDatabase):

  TABLE_NAME = 'covid_hosp_state_timeseries'

  # These are the names that appear in the CSV header, in order of appearance
  # in the database table, along with corresponding data type converters.
  # However, note that the corresponding database column names may be shorter
  # due to constraints on the length of column names. See
  # /src/ddl/covid_hosp.sql for more information.
  ORDERED_CSV_COLUMNS = [
    ('state', str),
    ('date', Utils.int_from_date),
    ('critical_staffing_shortage_today_yes', int),
    ('critical_staffing_shortage_today_no', int),
    ('critical_staffing_shortage_today_not_reported', int),
    ('critical_staffing_shortage_anticipated_within_week_yes', int),
    ('critical_staffing_shortage_anticipated_within_week_no', int),
    ('critical_staffing_shortage_anticipated_within_week_not_reported', int),
    ('hospital_onset_covid', int),
    ('hospital_onset_covid_coverage', int),
    ('inpatient_beds', int),
    ('inpatient_beds_coverage', int),
    ('inpatient_beds_used', int),
    ('inpatient_beds_used_coverage', int),
    ('inpatient_beds_used_covid', int),
    ('inpatient_beds_used_covid_coverage', int),
    ('previous_day_admission_adult_covid_confirmed', int),
    ('previous_day_admission_adult_covid_confirmed_coverage', int),
    ('previous_day_admission_adult_covid_suspected', int),
    ('previous_day_admission_adult_covid_suspected_coverage', int),
    ('previous_day_admission_pediatric_covid_confirmed', int),
    ('previous_day_admission_pediatric_covid_confirmed_coverage', int),
    ('previous_day_admission_pediatric_covid_suspected', int),
    ('previous_day_admission_pediatric_covid_suspected_coverage', int),
    ('staffed_adult_icu_bed_occupancy', int),
    ('staffed_adult_icu_bed_occupancy_coverage', int),
    ('staffed_icu_adult_patients_confirmed_and_suspected_covid', int),
    ('staffed_icu_adult_patients_confirmed_and_suspected_covid_coverage', int),
    ('staffed_icu_adult_patients_confirmed_covid', int),
    ('staffed_icu_adult_patients_confirmed_covid_coverage', int),
    ('total_adult_patients_hospitalized_confirmed_and_suspected_covid', int),
    ('total_adult_patients_hospitalized_confirmed_and_suspected_covid_coverage', int),
    ('total_adult_patients_hospitalized_confirmed_covid', int),
    ('total_adult_patients_hospitalized_confirmed_covid_coverage', int),
    ('total_pediatric_patients_hospitalized_confirmed_and_suspected_covid', int),
    ('total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_coverage', int),
    ('total_pediatric_patients_hospitalized_confirmed_covid', int),
    ('total_pediatric_patients_hospitalized_confirmed_covid_coverage', int),
    ('total_staffed_adult_icu_beds', int),
    ('total_staffed_adult_icu_beds_coverage', int),
    ('inpatient_beds_utilization', float),
    ('inpatient_beds_utilization_coverage', int),
    ('inpatient_beds_utilization_numerator', int),
    ('inpatient_beds_utilization_denominator', int),
    ('percent_of_inpatients_with_covid', float),
    ('percent_of_inpatients_with_covid_coverage', int),
    ('percent_of_inpatients_with_covid_numerator', int),
    ('percent_of_inpatients_with_covid_denominator', int),
    ('inpatient_bed_covid_utilization', float),
    ('inpatient_bed_covid_utilization_coverage', int),
    ('inpatient_bed_covid_utilization_numerator', int),
    ('inpatient_bed_covid_utilization_denominator', int),
    ('adult_icu_bed_covid_utilization', float),
    ('adult_icu_bed_covid_utilization_coverage', int),
    ('adult_icu_bed_covid_utilization_numerator', int),
    ('adult_icu_bed_covid_utilization_denominator', int),
    ('adult_icu_bed_utilization', float),
    ('adult_icu_bed_utilization_coverage', int),
    ('adult_icu_bed_utilization_numerator', int),
    ('adult_icu_bed_utilization_denominator', int),
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(
        *args,
        **kwargs,
        table_name=Database.TABLE_NAME,
        columns_and_types=Database.ORDERED_CSV_COLUMNS,
        additional_fields=('T',))
