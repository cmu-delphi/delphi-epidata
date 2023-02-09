from delphi.epidata.acquisition.covid_hosp.common.database import Columndef
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.facility.network import Network


class Database(BaseDatabase):

    TABLE_NAME = 'covid_hosp_facility'
    KEY_COLS = ['hospital_pk', 'collection_week']
    AGGREGATE_KEY_COLS = [
        'address',
        'ccn',
        'city',
        'fips_code',
        'geocoded_hospital_address',
        'hhs_ids',
        'hospital_name',
        'hospital_pk',
        'hospital_subtype',
        'is_metro_micro',
        'state',
        'zip'
    ]
    # These are 3-tuples of (
    #   CSV header name,
    #   SQL db column name,
    #   data type
    # ) for all the columns in the CSV file.
    # Note that the corresponding database column names may be shorter
    # due to constraints on the length of column names. See
    # /src/ddl/covid_hosp.sql for more information.
    ORDERED_CSV_COLUMNS = [
        Columndef('hospital_pk', 'hospital_pk', str),
        Columndef('collection_week', 'collection_week', Utils.int_from_date),
        Columndef('address', 'address', str),
        Columndef('all_adult_hospital_beds_7_day_avg', 'all_adult_hospital_beds_7_day_avg', float),
        Columndef('all_adult_hospital_beds_7_day_coverage', 'all_adult_hospital_beds_7_day_coverage', int),
        Columndef('all_adult_hospital_beds_7_day_sum', 'all_adult_hospital_beds_7_day_sum', int),
        Columndef('all_adult_hospital_inpatient_bed_occupied_7_day_avg', 'all_adult_hospital_inpatient_bed_occupied_7_day_avg', float),
        Columndef('all_adult_hospital_inpatient_bed_occupied_7_day_coverage', 'all_adult_hospital_inpatient_bed_occupied_7_day_coverage', int),
        Columndef('all_adult_hospital_inpatient_bed_occupied_7_day_sum', 'all_adult_hospital_inpatient_bed_occupied_7_day_sum', int),
        Columndef('all_adult_hospital_inpatient_beds_7_day_avg', 'all_adult_hospital_inpatient_beds_7_day_avg', float),
        Columndef('all_adult_hospital_inpatient_beds_7_day_coverage', 'all_adult_hospital_inpatient_beds_7_day_coverage', int),
        Columndef('all_adult_hospital_inpatient_beds_7_day_sum', 'all_adult_hospital_inpatient_beds_7_day_sum', int),
        Columndef('ccn', 'ccn', str),
        Columndef('city', 'city', str),
        Columndef('fips_code', 'fips_code', str),
        Columndef('geocoded_hospital_address', 'geocoded_hospital_address', str),
        Columndef('hhs_ids', 'hhs_ids', str),
        Columndef('hospital_name', 'hospital_name', str),
        Columndef('hospital_subtype', 'hospital_subtype', str),
        Columndef('icu_beds_used_7_day_avg', 'icu_beds_used_7_day_avg', float),
        Columndef('icu_beds_used_7_day_coverage', 'icu_beds_used_7_day_coverage', int),
        Columndef('icu_beds_used_7_day_sum', 'icu_beds_used_7_day_sum', int),
        Columndef('icu_patients_confirmed_influenza_7_day_avg', 'icu_patients_confirmed_influenza_7_day_avg', float),
        Columndef('icu_patients_confirmed_influenza_7_day_coverage', 'icu_patients_confirmed_influenza_7_day_coverage', int),
        Columndef('icu_patients_confirmed_influenza_7_day_sum', 'icu_patients_confirmed_influenza_7_day_sum', int),
        Columndef('inpatient_beds_7_day_avg', 'inpatient_beds_7_day_avg', float),
        Columndef('inpatient_beds_7_day_coverage', 'inpatient_beds_7_day_coverage', int),
        Columndef('inpatient_beds_7_day_sum', 'inpatient_beds_7_day_sum', int),
        Columndef('inpatient_beds_used_7_day_avg', 'inpatient_beds_used_7_day_avg', float),
        Columndef('inpatient_beds_used_7_day_coverage', 'inpatient_beds_used_7_day_coverage', int),
        Columndef('inpatient_beds_used_7_day_sum', 'inpatient_beds_used_7_day_sum', int),
        Columndef('is_corrected', 'is_corrected', Utils.parse_bool),
        Columndef('is_metro_micro', 'is_metro_micro', Utils.parse_bool),
        Columndef('previous_day_admission_adult_covid_confirmed_18-19_7_day_sum', 'previous_day_admission_adult_covid_confirmed_18_19_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_20-29_7_day_sum', 'previous_day_admission_adult_covid_confirmed_20_29_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_30-39_7_day_sum', 'previous_day_admission_adult_covid_confirmed_30_39_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_40-49_7_day_sum', 'previous_day_admission_adult_covid_confirmed_40_49_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_50-59_7_day_sum', 'previous_day_admission_adult_covid_confirmed_50_59_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_60-69_7_day_sum', 'previous_day_admission_adult_covid_confirmed_60_69_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_70-79_7_day_sum', 'previous_day_admission_adult_covid_confirmed_70_79_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_7_day_coverage', 'previous_day_admission_adult_covid_confirmed_7_day_coverage', int),
        Columndef('previous_day_admission_adult_covid_confirmed_7_day_sum', 'previous_day_admission_adult_covid_confirmed_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_80+_7_day_sum', 'previous_day_admission_adult_covid_confirmed_80plus_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_confirmed_unknown_7_day_sum', 'previous_day_admission_adult_covid_confirmed_unknown_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_18-19_7_day_sum', 'previous_day_admission_adult_covid_suspected_18_19_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_20-29_7_day_sum', 'previous_day_admission_adult_covid_suspected_20_29_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_30-39_7_day_sum', 'previous_day_admission_adult_covid_suspected_30_39_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_40-49_7_day_sum', 'previous_day_admission_adult_covid_suspected_40_49_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_50-59_7_day_sum', 'previous_day_admission_adult_covid_suspected_50_59_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_60-69_7_day_sum', 'previous_day_admission_adult_covid_suspected_60_69_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_70-79_7_day_sum', 'previous_day_admission_adult_covid_suspected_70_79_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_7_day_coverage', 'previous_day_admission_adult_covid_suspected_7_day_coverage', int),
        Columndef('previous_day_admission_adult_covid_suspected_7_day_sum', 'previous_day_admission_adult_covid_suspected_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_80+_7_day_sum', 'previous_day_admission_adult_covid_suspected_80plus_7_day_sum', int),
        Columndef('previous_day_admission_adult_covid_suspected_unknown_7_day_sum', 'previous_day_admission_adult_covid_suspected_unknown_7_day_sum', int),
        Columndef('previous_day_admission_influenza_confirmed_7_day_sum', 'previous_day_admission_influenza_confirmed_7_day_sum', int),
        Columndef('previous_day_admission_pediatric_covid_confirmed_7_day_coverage', 'previous_day_admission_pediatric_covid_confirmed_7_day_coverage', int),
        Columndef('previous_day_admission_pediatric_covid_confirmed_7_day_sum', 'previous_day_admission_pediatric_covid_confirmed_7_day_sum', int),
        Columndef('previous_day_admission_pediatric_covid_suspected_7_day_coverage', 'previous_day_admission_pediatric_covid_suspected_7_day_coverage', int),
        Columndef('previous_day_admission_pediatric_covid_suspected_7_day_sum', 'previous_day_admission_pediatric_covid_suspected_7_day_sum', int),
        Columndef('previous_day_covid_ED_visits_7_day_sum', 'previous_day_covid_ed_visits_7_day_sum', int),
        Columndef('previous_day_total_ED_visits_7_day_sum', 'previous_day_total_ed_visits_7_day_sum', int),
        Columndef('previous_week_patients_covid_vaccinated_doses_all_7_day', 'previous_week_patients_covid_vaccinated_doses_all_7_day', int),
        Columndef('previous_week_patients_covid_vaccinated_doses_all_7_day_sum', 'previous_week_patients_covid_vaccinated_doses_all_7_day_sum', int),
        Columndef('previous_week_patients_covid_vaccinated_doses_one_7_day', 'previous_week_patients_covid_vaccinated_doses_one_7_day', int),
        Columndef('previous_week_patients_covid_vaccinated_doses_one_7_day_sum', 'previous_week_patients_covid_vaccinated_doses_one_7_day_sum', int),
        Columndef('previous_week_personnel_covid_vaccinated_doses_administered_7_day', 'previous_week_personnel_covid_vaccd_doses_administered_7_day', int),
        Columndef(
            'previous_week_personnel_covid_vaccinated_doses_administered_7_day_sum',
            'previous_week_personnel_covid_vaccd_doses_administered_7_day_sum',
            int
        ),
        Columndef('staffed_adult_icu_bed_occupancy_7_day_avg', 'staffed_adult_icu_bed_occupancy_7_day_avg', float),
        Columndef('staffed_adult_icu_bed_occupancy_7_day_coverage', 'staffed_adult_icu_bed_occupancy_7_day_coverage', int),
        Columndef('staffed_adult_icu_bed_occupancy_7_day_sum', 'staffed_adult_icu_bed_occupancy_7_day_sum', int),
        Columndef('staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_avg', 'staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg', float),
        Columndef(
            'staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_coverage',
            'staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov',
            int
        ),
        Columndef('staffed_icu_adult_patients_confirmed_and_suspected_covid_7_day_sum', 'staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum', int),
        Columndef('staffed_icu_adult_patients_confirmed_covid_7_day_avg', 'staffed_icu_adult_patients_confirmed_covid_7_day_avg', float),
        Columndef('staffed_icu_adult_patients_confirmed_covid_7_day_coverage', 'staffed_icu_adult_patients_confirmed_covid_7_day_coverage', int),
        Columndef('staffed_icu_adult_patients_confirmed_covid_7_day_sum', 'staffed_icu_adult_patients_confirmed_covid_7_day_sum', int),
        Columndef('state', 'state', str),
        Columndef(
            'total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg',
            'total_adult_patients_hosp_confirmed_suspected_covid_7d_avg',
            float
        ),
        Columndef(
            'total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage',
            'total_adult_patients_hosp_confirmed_suspected_covid_7d_cov',
            int
        ),
        Columndef(
            'total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_sum',
            'total_adult_patients_hosp_confirmed_suspected_covid_7d_sum',
            int
        ),
        Columndef('total_adult_patients_hospitalized_confirmed_covid_7_day_avg', 'total_adult_patients_hospitalized_confirmed_covid_7_day_avg', float),
        Columndef(
            'total_adult_patients_hospitalized_confirmed_covid_7_day_coverage',
            'total_adult_patients_hospitalized_confirmed_covid_7_day_coverage',
            int
        ),
        Columndef('total_adult_patients_hospitalized_confirmed_covid_7_day_sum', 'total_adult_patients_hospitalized_confirmed_covid_7_day_sum', int),
        Columndef('total_beds_7_day_avg', 'total_beds_7_day_avg', float),
        Columndef('total_beds_7_day_coverage', 'total_beds_7_day_coverage', int),
        Columndef('total_beds_7_day_sum', 'total_beds_7_day_sum', int),
        Columndef('total_icu_beds_7_day_avg', 'total_icu_beds_7_day_avg', float),
        Columndef('total_icu_beds_7_day_coverage', 'total_icu_beds_7_day_coverage', int),
        Columndef('total_icu_beds_7_day_sum', 'total_icu_beds_7_day_sum', int),
        Columndef('total_patients_hospitalized_confirmed_influenza_7_day_avg', 'total_patients_hospitalized_confirmed_influenza_7_day_avg', float),
        Columndef('total_patients_hospitalized_confirmed_influenza_7_day_coverage', 'total_patients_hospitalized_confirmed_influenza_7_day_coverage', int),
        Columndef('total_patients_hospitalized_confirmed_influenza_7_day_sum', 'total_patients_hospitalized_confirmed_influenza_7_day_sum', int),
        Columndef('total_patients_hospitalized_confirmed_influenza_and_covid_7_day_avg', 'total_patients_hosp_confirmed_influenza_and_covid_7d_avg', float),
        Columndef(
            'total_patients_hospitalized_confirmed_influenza_and_covid_7_day_coverage',
            'total_patients_hosp_confirmed_influenza_and_covid_7d_cov',
            int),
        Columndef('total_patients_hospitalized_confirmed_influenza_and_covid_7_day_sum', 'total_patients_hosp_confirmed_influenza_and_covid_7d_sum', int),
        Columndef(
            'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg',
            'total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg',
            float),
        Columndef(
            'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_coverage',
            'total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov',
            int),
        Columndef(
            'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_7_day_sum',
            'total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum',
            int
        ),
        Columndef(
            'total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg',
            'total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg',
            float
        ),
        Columndef('total_pediatric_patients_hospitalized_confirmed_covid_7_day_coverage', 'total_pediatric_patients_hosp_confirmed_covid_7d_cov', int),
        Columndef('total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum', 'total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum', int),
        Columndef('total_personnel_covid_vaccinated_doses_all_7_day', 'total_personnel_covid_vaccinated_doses_all_7_day', int),
        Columndef('total_personnel_covid_vaccinated_doses_all_7_day_sum', 'total_personnel_covid_vaccinated_doses_all_7_day_sum', int),
        Columndef('total_personnel_covid_vaccinated_doses_none_7_day', 'total_personnel_covid_vaccinated_doses_none_7_day', int),
        Columndef('total_personnel_covid_vaccinated_doses_none_7_day_sum', 'total_personnel_covid_vaccinated_doses_none_7_day_sum', int),
        Columndef('total_personnel_covid_vaccinated_doses_one_7_day', 'total_personnel_covid_vaccinated_doses_one_7_day', int),
        Columndef('total_personnel_covid_vaccinated_doses_one_7_day_sum', 'total_personnel_covid_vaccinated_doses_one_7_day_sum', int),
        Columndef('total_staffed_adult_icu_beds_7_day_avg', 'total_staffed_adult_icu_beds_7_day_avg', float),
        Columndef('total_staffed_adult_icu_beds_7_day_coverage', 'total_staffed_adult_icu_beds_7_day_coverage', int),
        Columndef('total_staffed_adult_icu_beds_7_day_sum', 'total_staffed_adult_icu_beds_7_day_sum', int),
        Columndef('zip', 'zip', str),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            table_name=Database.TABLE_NAME,
            hhs_dataset_id=Network.DATASET_ID,
            key_columns=Database.KEY_COLS,
            columns_and_types=Database.ORDERED_CSV_COLUMNS
        )
