# This is a helper script for updating the signal spreadsheet "Other Endpoints Signals" tab
# (https://docs.google.com/spreadsheets/d/1zb7ItJzY5oq1n-2xtvnPBiJu2L3AqmCKubrLkKJZVHs/edit?gid=1364181703#gid=1364181703)
# semi-programmatically.
#
# To run this, you need to have the "Other Endpoints Signals" tab and the "Other
# Endpoints Data Sources" tabs saved locally as CSVs. The script loads and
# modifies the data from the Signals tab.
#
# To update a given field, we define a map between data source names and a set
# of values, use the data source column to index into the map, and save the
# result to the spreadsheet. There is some additional logic, depending on the
# field to be updated, to handle certain signals and cases (active/inactive
# signals) separately.
#
# The updated spreadsheet is saved to disk as a CSV. Any updated columns must be
# manually pasted into the online spreadsheet. This script checks that the
# original sort order is the same as that of the updated spreadsheet.


# Load packages
suppressPackageStartupMessages({
  library(epidatr) # Access Delphi API
  library(dplyr) # Data handling
  library(readr) # Import csv sheet
  library(pipeR) # special pipe %>>%
  library(glue) # f-string formatting
})

options(warn = 1)



# read in "Other Endpoints Signals" table as csv
#   source subdivision is in "source_sub" col
#   data signal is in "signal" col
#   start date is in "temp_start" col
#   end date is in "temp_end" col
signal_sheet <- suppressMessages(read_csv("delphi-eng-covidcast-data-sources-signals_-_Other_Endpoint_Signals.csv")) %>%
  # Drop empty rows
  filter(!is.na(`Source Subdivision`) ) #& !is.na(Signal)) # `Signal` makes extra certain data is missing


# read in "Other Endpoints Data Sources" table as csv
# shows how real data source names map to "source subdivisions"
#   data source is in "DB Source" col
#   source subdivision is in "source_sub" col
source_map <- suppressMessages(read_csv("delphi-eng-covidcast-data-sources-signals_-_Other_Endpoint_Data_Sources.csv")) %>%
  # Drop empty rows
  filter(!is.na(`Source Subdivision`)) %>%
  select(`Source Subdivision`, Link, `Private/Public`)

# left join metadata_subset with source_map
output <- left_join(
  signal_sheet,
  source_map,
  by = "Source Subdivision"
)


signals <- tibble::tribble(
  ~data_source, ~signal, ~description, ~include_in_signal_discovery_app,
  
  "covid_hosp_state_timeseries", "issue", "the day (YYYYMMDD) that the dataset was published", FALSE,
  "covid_hosp_state_timeseries", "state", "The two character state code", FALSE,
  "covid_hosp_state_timeseries", "date", "the day (YYYYMMDD) to which the data applies. For data taken from daily snapshot files, the `date` field is filled from the provided `reporting_cutoff_start` value, defined as 'Look back date start - The latest reports from each hospital is summed for this report starting with this date.'", FALSE,
  "covid_hosp_state_timeseries", "adult_icu_bed_covid_utilization", "Percentage of total staffed adult ICU beds currently utilized by patients who have suspected or confirmed COVID-19 in this state. This number only accounts for hospitals in the state that report both 'staffed_icu_adult_patients_confirmed_suspected_covid' and 'total_staffed_adult_icu_beds' fields.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_covid_utilization_coverage", "Number of hospitals reporting both both 'staffed_icu_adult_patients_confirmed_suspected_covid' and 'total_staffed_adult_icu_beds'.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_covid_utilization_denominator", "Sum of 'total_staffed_adult_icu_beds' for hospitals reporting both 'staffed_icu_adult_patients_confirmed_suspected_covid' and 'total_staffed_adult_icu_beds'.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_covid_utilization_numerator", "Sum of 'staffed_icu_adult_patients_confirmed_suspected_covid' for hospitals reporting both 'staffed_icu_adult_patients_confirmed_suspected_covid' and 'total_staffed_adult_icu_beds'.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_utilization", "Percentage of staffed adult ICU beds that are being utilized in this state. This number only accounts for hospitals in the state that report both 'staffed_adult_icu_bed_occupancy' and 'total_staffed_adult_icu_beds' fields.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_utilization_coverage", "Number of hospitals reporting both both 'staffed_adult_icu_bed_occupancy' and 'total_staffed_adult_icu_beds'.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_utilization_denominator", "Sum of 'total_staffed_adult_icu_beds' for hospitals reporting both 'staffed_adult_icu_bed_occupancy' and 'total_staffed_adult_icu_beds'.", TRUE,
  "covid_hosp_state_timeseries", "adult_icu_bed_utilization_numerator", "Sum of 'staffed_adult_icu_bed_occupancy' for hospitals reporting both 'staffed_adult_icu_bed_occupancy' and 'total_staffed_adult_icu_beds'.", TRUE,
  "covid_hosp_state_timeseries", "critical_staffing_shortage_anticipated_within_week_no", "Number of hospitals reporting that they do not anticipate a critical staffing shortage within a week in this state.", TRUE,
  "covid_hosp_state_timeseries", "critical_staffing_shortage_anticipated_within_week_not_reported", "Number of hospitals not reporting staffing shortage within week status in this state.", TRUE,
  "covid_hosp_state_timeseries", "critical_staffing_shortage_anticipated_within_week_yes", "Number of hospitals reporting that they anticipate a critical staffing shortage within a week in this state.", TRUE,
  "covid_hosp_state_timeseries", "critical_staffing_shortage_today_no", "Number of hospitals reporting as not having a critical staffing shortage today in this state.", TRUE,
  "covid_hosp_state_timeseries", "critical_staffing_shortage_today_not_reported", "Number of hospitals not reporting staffing shortage today status in this state.", TRUE,
  "covid_hosp_state_timeseries", "critical_staffing_shortage_today_yes", "Number of hospitals reporting a critical staffing shortage today in this state.", TRUE,
  "covid_hosp_state_timeseries", "hospital_onset_covid", "Total current inpatients with onset of suspected or laboratory-confirmed COVID-19 fourteen or more days after admission for a condition other than COVID-19 in this state.", TRUE,
  "covid_hosp_state_timeseries", "hospital_onset_covid_coverage", "Number of hospitals reporting 'hospital_onset_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_bed_covid_utilization", "Percentage of total (used/available) inpatient beds currently utilized by patients who have suspected or confirmed COVID-19 in this state. This number only accounts for hospitals in the state that report both 'inpatient_beds_used_covid' and 'inpatient_beds' fields.", TRUE,
  "covid_hosp_state_timeseries", "inpatient_bed_covid_utilization_coverage", "Number of hospitals reporting both 'inpatient_beds_used_covid' and 'inpatient_beds'.", TRUE,
  "covid_hosp_state_timeseries", "inpatient_bed_covid_utilization_denominator", "Sum of 'inpatient_beds' for hospitals reporting both 'inpatient_beds_used_covid' and 'inpatient_beds'.", TRUE,
  "covid_hosp_state_timeseries", "inpatient_bed_covid_utilization_numerator", "Sum of 'inpatient_beds_used_covid' for hospitals reporting both 'inpatient_beds_used_covid' and 'inpatient_beds'.", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds", "Reported total number of staffed inpatient beds including all overflow and surge/expansion beds used for inpatients (includes all ICU beds) in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_coverage", "Number of hospitals reporting 'inpatient_beds' in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_used", "Reported total number of staffed inpatient beds that are occupied in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_used_coverage", "Number of hospitals reporting 'inpatient_beds_used' in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_used_covid", "Reported patients currently hospitalized in an inpatient bed who have suspected or confirmed COVID-19 in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_used_covid_coverage", "Number of hospitals reporting 'inpatient_beds_used_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_utilization", "Percentage of inpatient beds that are being utilized in this state. This number only accounts for hospitals in the state that report both 'inpatient_beds_used' and 'inpatient_beds' fields.", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_utilization_coverage", "Number of hospitals reporting both 'inpatient_beds_used' and 'inpatient_beds'", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_utilization_denominator", "Sum of 'inpatient_beds' for hospitals reporting both 'inpatient_beds_used' and 'inpatient_beds'", TRUE,
  "covid_hosp_state_timeseries", "inpatient_beds_utilization_numerator", "Sum of 'inpatient_beds_used' for hospitals reporting both 'inpatient_beds_used' and 'inpatient_beds'", TRUE,
  "covid_hosp_state_timeseries", "percent_of_inpatients_with_covid", "Percentage of inpatient population who have suspected or confirmed COVID-19 in this state. This number only accounts for hospitals in the state that report both 'inpatient_beds_used_covid' and 'inpatient_beds_used' fields.", TRUE,
  "covid_hosp_state_timeseries", "percent_of_inpatients_with_covid_coverage", "Number of hospitals reporting both 'inpatient_beds_used_covid' and 'inpatient_beds_used'.", TRUE,
  "covid_hosp_state_timeseries", "percent_of_inpatients_with_covid_denominator", "Sum of 'inpatient_beds_used' for hospitals reporting both 'inpatient_beds_used_covid' and 'inpatient_beds_used'.", TRUE,
  "covid_hosp_state_timeseries", "percent_of_inpatients_with_covid_numerator", "Sum of 'inpatient_beds_used_covid' for hospitals reporting both 'inpatient_beds_used_covid' and 'inpatient_beds_used'.", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed", "Number of patients who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_coverage", "Number of hospitals reporting 'previous_day_admission_adult_covid_confirmed' in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected", "Number of patients who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_coverage", "Number of hospitals reporting 'previous_day_admission_adult_covid_suspected' in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_pediatric_covid_confirmed", "Number of pediatric patients who were admitted to an inpatient bed, including NICU, PICU, newborn, and nursery, on the previous calendar day who had confirmed COVID-19 at the time of admission in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_pediatric_covid_confirmed_coverage", "Number of hospitals reporting 'previous_day_admission_pediatric_covid_confirmed' in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_pediatric_covid_suspected", "Number of pediatric patients who were admitted to an inpatient bed, including NICU, PICU, newborn, and nursery, on the previous calendar day who had suspected COVID-19 at the time of admission in this state", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_pediatric_covid_suspected_coverage", "Number of hospitals reporting 'previous_day_admission_pediatric_covid_suspected' in this state", TRUE,
  "covid_hosp_state_timeseries", "staffed_adult_icu_bed_occupancy", "Reported total number of staffed inpatient adult ICU beds that are occupied in this state", TRUE,
  "covid_hosp_state_timeseries", "staffed_adult_icu_bed_occupancy_coverage", "Number of hospitals reporting 'staffed_adult_icu_bed_occupancy' in this state", TRUE,
  "covid_hosp_state_timeseries", "staffed_icu_adult_patients_confirmed_suspected_covid", "Reported patients currently hospitalized in an adult ICU bed who have suspected or confirmed COVID-19 in this state", TRUE,
  "covid_hosp_state_timeseries", "staffed_icu_adult_patients_confirmed_suspected_covid_coverage", "Number of hospitals reporting 'staffed_icu_adult_patients_confirmed_suspected_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "staffed_icu_adult_patients_confirmed_covid", "Reported patients currently hospitalized in an adult ICU bed who have confirmed COVID-19 in this state", TRUE,
  "covid_hosp_state_timeseries", "staffed_icu_adult_patients_confirmed_covid_coverage", "Number of hospitals reporting 'staffed_icu_adult_patients_confirmed_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "total_adult_patients_hosp_confirmed_suspected_covid", "Reported patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed or suspected COVID-19. This include those in observation beds.", TRUE,
  "covid_hosp_state_timeseries", "total_adult_patients_hosp_confirmed_suspected_covid_coverage", "Number of hospitals reporting 'total_adult_patients_hosp_confirmed_suspected_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "total_adult_patients_hosp_confirmed_covid", "Reported patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed COVID-19. This include those in observation beds.", TRUE,
  "covid_hosp_state_timeseries", "total_adult_patients_hosp_confirmed_covid_coverage", "Number of hospitals reporting 'total_adult_patients_hosp_confirmed_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "total_pediatric_patients_hosp_confirmed_suspected_covid", "Reported patients currently hospitalized in a pediatric inpatient bed, including NICU, newborn, and nursery, who are suspected or laboratory-confirmed-positive for COVID-19. This include those in observation beds.", TRUE,
  "covid_hosp_state_timeseries", "total_pediatric_patients_hosp_confirmed_suspected_covid_coverage", "Number of hospitals reporting 'total_pediatric_patients_hosp_confirmed_suspected_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "total_pediatric_patients_hosp_confirmed_covid", "Reported patients currently hospitalized in a pediatric inpatient bed, including NICU, newborn, and nursery, who are laboratory-confirmed-positive for COVID-19. This include those in observation beds.", TRUE,
  "covid_hosp_state_timeseries", "total_pediatric_patients_hosp_confirmed_covid_coverage", "Number of hospitals reporting 'total_pediatric_patients_hosp_confirmed_covid' in this state", TRUE,
  "covid_hosp_state_timeseries", "total_staffed_adult_icu_beds", "Reported total number of staffed inpatient adult ICU beds in this state", TRUE,
  "covid_hosp_state_timeseries", "total_staffed_adult_icu_beds_coverage", "Number of hospitals reporting 'total_staffed_adult_icu_beds' in this state", TRUE,
  "covid_hosp_state_timeseries", "record_type", "Specifies if a row came from a time series file or a daily snapshot file. 'T' = time series and 'D' =  daily snapshot. When both a time series and a daily snapshot row have the same issue/date/state but different values, we tiebreak by taking the daily snapshot value.", TRUE,
  "covid_hosp_state_timeseries", "geocoded_state","", FALSE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_18_19","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_18_19_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_20_29","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_20_29_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_30_39","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_30_39_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_40_49","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_40_49_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_50_59","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_50_59_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_60_69","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_60_69_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_70_79","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_70_79_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_80plus","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_80plus_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_unknown","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_confirmed_unknown_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_18_19","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_18_19_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_20_29","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_20_29_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_30_39","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_30_39_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_40_49","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_40_49_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_50_59","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_50_59_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_60_69","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_60_69_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_70_79","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_70_79_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_80plus","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_80plus_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_unknown","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_adult_covid_suspected_unknown_coverage","", TRUE,
  "covid_hosp_state_timeseries", "deaths_covid","", TRUE,
  "covid_hosp_state_timeseries", "deaths_covid_coverage","", TRUE,
  "covid_hosp_state_timeseries", "on_hand_supply_therapeutic_a_casirivimab_imdevimab_courses","", TRUE,
  "covid_hosp_state_timeseries", "on_hand_supply_therapeutic_b_bamlanivimab_courses","", TRUE,
  "covid_hosp_state_timeseries", "on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses","", TRUE,
  "covid_hosp_state_timeseries", "previous_week_therapeutic_a_casirivimab_imdevimab_courses_used","", TRUE,
  "covid_hosp_state_timeseries", "previous_week_therapeutic_b_bamlanivimab_courses_used","", TRUE,
  "covid_hosp_state_timeseries", "previous_week_therapeutic_c_bamlanivimab_etesevimab_courses_used","", TRUE,
  "covid_hosp_state_timeseries", "icu_patients_confirmed_influenza","", TRUE,
  "covid_hosp_state_timeseries", "icu_patients_confirmed_influenza_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_influenza_confirmed","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_admission_influenza_confirmed_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_deaths_covid_and_influenza","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_deaths_covid_and_influenza_coverage","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_deaths_influenza","", TRUE,
  "covid_hosp_state_timeseries", "previous_day_deaths_influenza_coverage","", TRUE,
  "covid_hosp_state_timeseries", "total_patients_hospitalized_confirmed_influenza","", TRUE,
  "covid_hosp_state_timeseries", "total_patients_hospitalized_confirmed_influenza_covid","", TRUE,
  "covid_hosp_state_timeseries", "total_patients_hospitalized_confirmed_influenza_covid_coverage","", TRUE,
  "covid_hosp_state_timeseries", "total_patients_hospitalized_confirmed_influenza_coverage","", TRUE,
  
  "covid_hosp_facility", "publication_date", "the day (YYYYMMDD) that the dataset was published. equivalent to `issue` in the state timeseries and metadata tables, but renamed here for clarity.", FALSE,
  "covid_hosp_facility", "hospital_pk", "This unique key for the given hospital that will match the ccn column if it exists, otherwise, it is a derived unique key.", FALSE,
  "covid_hosp_facility", "collection_week", "The first day (YYYYMMDD) of the week to which the data applies. This is a weekly rollup of daily data from Friday to Thursday. as a result, we can't use Sunday-to-Saturday epiweeks (YYYYMM) to identify the week, so we instead use the date of Friday, as is done in the upstream data source.", FALSE,
  "covid_hosp_facility", "state", "The two digit state/territory code for the hospital.", FALSE,
  "covid_hosp_facility", "ccn", "CMS Certification Number (CCN) of the given facility ", FALSE,
  "covid_hosp_facility", "hospital_name", "The name of the facility reporting.", FALSE,
  "covid_hosp_facility", "address", "The address of the facility reporting.", FALSE,
  "covid_hosp_facility", "geocoded_hospital_address", "Location of facility given in longitude-latitude coordinates", FALSE,
  "covid_hosp_facility", "hhs_ids", "", FALSE,
  "covid_hosp_facility", "city", "The city of the facility reporting.", FALSE,
  "covid_hosp_facility", "zip", "The 5-digit zip code of the facility reporting.", FALSE,
  "covid_hosp_facility", "hospital_subtype", "The sub-type of the facility reporting. Valid values are: Children's Hospitals, Critical Access Hospitals, Long Term, Psychiatric, Rehabilitation & Short Term. Some facilities are not designated with this field.", FALSE,
  "covid_hosp_facility", "fips_code", "The Federal Information Processing Standard (FIPS) code of the location of the hospital.", FALSE,
  "covid_hosp_facility", "is_metro_micro", "This is based on whether the facility serves a Metropolitan or Micropolitan area. True if yes, and false if no.", FALSE,
  "covid_hosp_facility", "total_beds_7_day_avg", "Average of total number of all staffed inpatient and outpatient beds in the hospital, including all overflow, observation, and active surge/expansion beds used for inpatients and for outpatients (including all ICU, ED, and observation) reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_beds_7_day_avg", "Average of all staffed inpatient and outpatient adult beds in the hospital, including all overflow and active surge/expansion beds for inpatients and for outpatients (including all ICU, ED, and observation) reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_inpatient_beds_7_day_avg", "Average of total number of staffed inpatient adult beds in the hospital including all overflow and active surge/expansion beds used for inpatients (including all designated ICU beds) reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "inpatient_beds_used_7_day_avg", "Average of total number of staffed inpatient beds that are occupied reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_inpatient_bed_occupied_7_day_avg", "Average of total number of staffed inpatient adult beds that are occupied reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "total_adult_patients_hosp_confirmed_suspected_covid_7d_avg", "Average number of patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed or suspected COVID19, including those in observation beds reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "total_adult_patients_hospitalized_confirmed_covid_7_day_avg", "Average number of patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed COVID-19, including those in observation beds. This average includes patients who have both laboratory-confirmed COVID-19 and laboratory-confirmed influenza.", TRUE,
  "covid_hosp_facility", "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg", "Average number of patients currently hospitalized in a pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who are suspected or laboratory-confirmed-positive for COVID-19. This average includes those in observation beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg", "Average number of patients currently hospitalized in a pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who have laboratory-confirmed COVID-19. Including those in observation beds. Including patients who have both laboratory-confirmed COVID-19 and laboratory confirmed influenza in this field reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "inpatient_beds_7_day_avg", "Average number of total number of staffed inpatient beds in your hospital including all overflow, observation, and active surge/expansion beds used for inpatients (including all ICU beds) reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_icu_beds_7_day_avg", "Average of total number of staffed inpatient ICU beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_staffed_adult_icu_beds_7_day_avg", "Average number of total number of staffed inpatient ICU beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "icu_beds_used_7_day_avg", "Average number of total number of staffed inpatient ICU beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "staffed_adult_icu_bed_occupancy_7_day_avg", "Average of total number of staffed inpatient adult ICU beds that are occupied reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg", "Average number of patients currently hospitalized in a designated adult ICU bed who have suspected or laboratory-confirmed COVID-19 reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "staffed_icu_adult_patients_confirmed_covid_7_day_avg", "Average number of patients currently hospitalized in a designated adult ICU bed who have laboratory-confirmed COVID-19. Including patients who have both laboratory-confirmed COVID-19 and laboratory-confirmed influenza in this field reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_patients_hospitalized_confirmed_influenza_7_day_avg", "umber of patients (all ages) currently hospitalized in an inpatient bed who have laboratory-confirmed influenza. Including those in observation beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "icu_patients_confirmed_influenza_7_day_avg", "Average of patients (all ages) currently hospitalized in a designated ICU bed with laboratory-confirmed influenza in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_patients_hosp_confirmed_influenza_and_covid_7d_avg", "umber of patients (all ages) currently hospitalized in an inpatient bed who have laboratory-confirmed COVID-19 and laboratory-confirmed influenza reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_beds_7_day_sum", "Sum of reports of total number of all staffed inpatient and outpatient beds in the hospital, including all overflow, observation, and active surge/expansion beds used for inpatients and for outpatients (including all ICU, ED, and observation) reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_beds_7_day_sum", "Sum of reports of all staffed inpatient and outpatient adult beds in the hospital, including all overflow and active surge/expansion beds for inpatients and for outpatients (including all ICU, ED, and observation) reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_inpatient_beds_7_day_sum", "Sum of reports of all staffed inpatient and outpatient adult beds in the hospital, including all overflow and active surge/expansion beds for inpatients and for outpatients (including all ICU, ED, and observation) reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "inpatient_beds_used_7_day_sum", "Sum of reports of total number of staffed inpatient beds that are occupied reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_inpatient_bed_occupied_7_day_sum", "Sum of reports of total number of staffed inpatient adult beds that are occupied reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "total_adult_patients_hosp_confirmed_suspected_covid_7d_sum", "Sum of reports of patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed or suspected COVID19. Including those in observation beds reported during the 7-day period.", TRUE,
  "covid_hosp_facility", "total_adult_patients_hospitalized_confirmed_covid_7_day_sum", "Sum of reports of patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed COVID-19. Including those in observation beds. Including patients who have both laboratory-confirmed COVID-19 and laboratory confirmed influenza in this field during the 7-day period.", TRUE,
  "covid_hosp_facility", "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum", "Sum of reports of patients currently hospitalized in a pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who are suspected or laboratory-confirmed-positive for COVID-19. Including those in observation beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum", "Sum of reports of patients currently hospitalized in a pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who have laboratory-confirmed COVID-19. Including those in observation beds. Including patients who have both laboratory-confirmed COVID-19 and laboratory confirmed influenza in this field reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "inpatient_beds_7_day_sum", "Sum of reports of total number of staffed inpatient beds in your hospital including all overflow, observation, and active surge/expansion beds used for inpatients (including all ICU beds) reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_icu_beds_7_day_sum", "Sum of reports of total number of staffed inpatient ICU beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_staffed_adult_icu_beds_7_day_sum", "Sum of reports of total number of staffed inpatient adult ICU beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "icu_beds_used_7_day_sum", "Sum of reports of total number of staffed inpatient ICU beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "staffed_adult_icu_bed_occupancy_7_day_sum", "Sum of reports of total number of staffed inpatient adult ICU beds that are occupied reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum", "Sum of reports of patients currently hospitalized in a designated adult ICU bed who have suspected or laboratory-confirmed COVID-19 reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "staffed_icu_adult_patients_confirmed_covid_7_day_sum", "Sum of reports of patients currently hospitalized in a designated adult ICU bed who have laboratory-confirmed COVID-19. Including patients who have both laboratory-confirmed COVID-19 and laboratory-confirmed influenza in this field reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_patients_hospitalized_confirmed_influenza_7_day_sum", "Sum of reports of patients (all ages) currently hospitalized in an inpatient bed who have laboratory-confirmed influenza. Including those in observation beds reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "icu_patients_confirmed_influenza_7_day_sum", "Sum of reports of patients (all ages) currently hospitalized in a designated ICU bed with laboratory-confirmed influenza reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_patients_hosp_confirmed_influenza_and_covid_7d_sum", "Sum of reports of patients (all ages) currently hospitalized in an inpatient bed who have laboratory-confirmed COVID-19 and laboratory-confirmed influenza reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "total_beds_7_day_coverage", "Number of times in the 7 day period that the facility reported total number of all staffed inpatient and outpatient beds in your hospital, including all overflow, observation, and active surge/expansion beds used for inpatients and for outpatients (including all ICU, ED, and observation)", TRUE,
  "covid_hosp_facility", "all_adult_hospital_beds_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of all staffed inpatient and outpatient adult beds in your hospital, including all overflow and active surge/expansion beds for inpatients and for outpatients (including all ICU, ED, and observation)", TRUE,
  "covid_hosp_facility", "all_adult_hospital_inpatient_beds_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient adult beds in your hospital including all overflow and active surge/expansion beds used for inpatients (including all designated ICU beds)", TRUE,
  "covid_hosp_facility", "inpatient_beds_used_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient beds that are occupied.", TRUE,
  "covid_hosp_facility", "all_adult_hospital_inpatient_bed_occupied_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient adult beds that are occupied.", TRUE,
  "covid_hosp_facility", "total_adult_patients_hosp_confirmed_suspected_covid_7d_cov", "Number of times in the 7-day period that the facility reported patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed or suspected COVID19. Including those in observation beds.", TRUE,
  "covid_hosp_facility", "total_adult_patients_hospitalized_confirmed_covid_7_day_coverage", "Number of times in the 7-day period that the facility reported patients currently hospitalized in an adult inpatient bed who have laboratory-confirmed COVID-19. Including those in observation beds. Including patients who have both laboratory-confirmed COVID-19 and laboratory confirmed influenza in this field.", TRUE,
  "covid_hosp_facility", "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov", "Number of times in the 7-day period that the facility reported Patients currently hospitalized in a pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who are suspected or laboratory-confirmed-positive for COVID-19. Including those in observation beds.", TRUE,
  "covid_hosp_facility", "total_pediatric_patients_hosp_confirmed_covid_7d_cov", "Number of times in the 7-day period that the facility reported patients currently hospitalized in a pediatric inpatient bed, including NICU, PICU, newborn, and nursery, who have laboratory-confirmed COVID-19. Including those in observation beds. Including patients who have both laboratory-confirmed COVID-19 and laboratory confirmed influenza in this field.", TRUE,
  "covid_hosp_facility", "inpatient_beds_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient beds in your hospital including all overflow, observation, and active surge/expansion beds used for inpatients (including all ICU beds)", TRUE,
  "covid_hosp_facility", "total_icu_beds_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient ICU beds.", TRUE,
  "covid_hosp_facility", "total_staffed_adult_icu_beds_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient adult ICU beds.", TRUE,
  "covid_hosp_facility", "icu_beds_used_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient ICU beds.", TRUE,
  "covid_hosp_facility", "staffed_adult_icu_bed_occupancy_7_day_coverage", "Number of times in the 7-day period that the facility reported total number of staffed inpatient adult ICU beds that are occupied.", TRUE,
  "covid_hosp_facility", "staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov", "Number of times in the 7-day period that the facility reported patients currently hospitalized in a designated adult ICU bed who have suspected or laboratory-confirmed COVID-19.", TRUE,
  "covid_hosp_facility", "staffed_icu_adult_patients_confirmed_covid_7_day_coverage", "Number of times in the 7-day period that the facility reported patients currently hospitalized in a designated adult ICU bed who have laboratory-confirmed COVID-19. Including patients who have both laboratory-confirmed COVID-19 and laboratory-confirmed influenza in this field.", TRUE,
  "covid_hosp_facility", "total_patients_hospitalized_confirmed_influenza_7_day_coverage", "Number of times in the 7-day period that the facility reported patients (all ages) currently hospitalized in an inpatient bed who have laboratory-confirmed influenza. Including those in observation beds.", TRUE,
  "covid_hosp_facility", "icu_patients_confirmed_influenza_7_day_coverage", "Number of times in the 7-day period that the facility reported patients (all ages) currently hospitalized in a designated ICU bed with laboratory-confirmed influenza.", TRUE,
  "covid_hosp_facility", "total_patients_hosp_confirmed_influenza_and_covid_7d_cov", "Number of times in the 7-day period that the facility reported patients (all ages) currently hospitalized in an inpatient bed who have laboratory-confirmed COVID-19 and laboratory-confirmed influenza.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_7_day_sum", "Sum of number of patients who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_18_19_7_day_sum", "Sum of number of patients age 18-19 who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_20_29_7_day_sum", "Sum of number of patients age 20-29 who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_30_39_7_day_sum", "Sum of number of patients age 30-39 who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_40_49_7_day_sum", "Sum of number of patients age 40-49 who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_50_59_7_day_sum", "Sum of number of patients age 50-59 who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_60_69_7_day_sum", "Sum of number of patients age 60-69 who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_70_79_7_day_sum", "Sum of number of patients age 70-79 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_80plus_7_day_sum", "Sum of number of patients 80 or older who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_confirmed_unknown_7_day_sum", "Sum of number of patients age unknown who were admitted to an adult inpatient bed on the previous calendar day who had confirmed COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_pediatric_covid_confirmed_7_day_sum", "Sum of number of pediatric patients who were admitted to an inpatient bed, including NICU, PICU, newborn, and nursery, on the previous calendar day who had confirmed COVID-19 at the time of admission.", TRUE,
  "covid_hosp_facility", "previous_day_covid_ed_visits_7_day_sum", "Sum of total number of ED visits who were seen on the previous calendar day who had a visit related to COVID-19 (meets suspected or confirmed definition or presents for COVID diagnostic testing – do not count patients who present for pre-procedure screening) reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_7_day_sum", "Sum of number of patients who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_18_19_7_day_sum", "Sum of number of patients age 18-19 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_20_29_7_day_sum", "Sum of number of patients age 20-29 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_30_39_7_day_sum", "Sum of number of patients age 30-39 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_40_49_7_day_sum", "Sum of number of patients age 40-49 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_50_59_7_day_sum", "Sum of number of patients age 50-59 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_60_69_7_day_sum", "Sum of number of patients age 60-69 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_70_79_7_day_sum", "Sum of number of patients age 70-79 who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_80plus_7_day_sum", "Sum of number of patients 80 or older who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_adult_covid_suspected_unknown_7_day_sum", "Sum of number of patients age unknown who were admitted to an adult inpatient bed on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_pediatric_covid_suspected_7_day_sum", "Sum of number of pediatrics patients who were admitted to an inpatient bed, including NICU, PICU, newborn, and nursery, on the previous calendar day who had suspected COVID-19 at the time of admission reported in 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_total_ed_visits_7_day_sum", "Sum of total number of patient visits to the ED who were seen on the previous calendar day regardless of reason for visit. Including all patients who are triaged even if they leave before being seen by a provider reported in the 7-day period.", TRUE,
  "covid_hosp_facility", "previous_day_admission_influenza_confirmed_7_day_sum", "Sum of number of patients (all ages) who were admitted to an inpatient bed on the previous calendar day who had laboratory-confirmed influenza at the time of admission reported in 7-day period.", TRUE,  
  
  "covid_hosp_facility_lookup", "address", "The address of the facility reporting.", FALSE,
  "covid_hosp_facility_lookup", "ccn", "CMS Certification Number (CCN) of the given facility ", FALSE,
  "covid_hosp_facility_lookup", "city", "The city of the facility reporting.", FALSE,
  "covid_hosp_facility_lookup", "fips_code", "The Federal Information Processing Standard (FIPS) code of the location of the hospital.", FALSE,
  "covid_hosp_facility_lookup", "hospital_name", "The name of the facility reporting.", FALSE,
  "covid_hosp_facility_lookup", "hospital_pk", "This unique key for the given hospital that will match the ccn column if it exists, otherwise, it is a derived unique key.", FALSE,
  "covid_hosp_facility_lookup", "hospital_subtype", "The sub-type of the facility reporting. Valid values are: Children's Hospitals, Critical Access Hospitals, Long Term, Psychiatric, Rehabilitation & Short Term. Some facilities are not designated with this field.", FALSE,
  "covid_hosp_facility_lookup", "is_metro_micro", "This is based on whether the facility serves a Metropolitan or Micropolitan area. True if yes, and false if no.", FALSE,
  "covid_hosp_facility_lookup", "state", "The two digit state/territory code for the hospital.", FALSE,
  "covid_hosp_facility_lookup", "zip", "The 5-digit zip code of the facility reporting.", FALSE,
)
























inactive_signals <- tibble::tribble(
  ~data_source, ~signal,
  
  "quidel", "raw_pct_negative",
  "quidel", "smoothed_pct_negative",
  "quidel", "raw_tests_per_device",
  "quidel", "smoothed_tests_per_device",
  
  "hospital-admissions", "smoothed_covid19",
  "hospital-admissions", "smoothed_adj_covid19",
  
  "google-symptoms", "anosmia_raw_search",
  "google-symptoms", "anosmia_smoothed_search",
  "google-symptoms", "ageusia_raw_search",
  "google-symptoms", "ageusia_smoothed_search",
  "google-symptoms", "sum_anosmia_ageusia_raw_search",
  "google-symptoms", "sum_anosmia_ageusia_smoothed_search"
)
inactive_signals$active <- FALSE

source55 <- left_join(
  source5, inactive_signals,
  by = c("Signal" = "signal", "data_source")
) %>%
  mutate(active = coalesce(active, !(data_source %in% inactive_sources)))



col <- "Geographic Scope"
# List all the highest-level locations for which the signal is available.
# Each location should b fully disambiguated as in the examples below.
# Muliple locations, if any, should be separated by a semicolon.
# E.g.:
#    If it's available for all (or almost all) of the US (whether by county, by state or only nationally), enter "USA".
#    If it's available only for the state of PA (whether by county, or only for the whole state), enter, "Pennsylvania, USA".
#    If it's available only for the states of PA and OH, enter, "Pennsylvania, USA; Ohio, USA"
#    If it's available only for Allegheny County, PA, enter "Allegheny, Pennsylvania, USA"
#    etc.
geo_scope <- c(
  "chng" = "USA",
  "covid-act-now" = "USA",
  "doctor-visits" = "USA",
  "dsew-cpr" = "USA",
  "fb-survey" = "USA",
  "ght" = "USA",
  "google-survey" = "USA",
  "google-symptoms" = "USA",
  "hhs" = "USA",
  "hospital-admissions" = "USA",
  "indicator-combination" = "USA",
  "jhu-csse" = "USA",
  "nchs-mortality" = "USA",
  "quidel" = "USA",
  "safegraph" = "USA",
  "usa-facts" = "USA",
  "youtube-survey" = "USA"
)
source_updated[, col] <- geo_scope[source_updated$data_source]




col <- "Available Geography"
# List all available geo-levels, e.g:  county,state,nation

# # Tool: Create lists of geos for each data source-signal combo based on what is
# # reported in metadata (does not include quidel).
# metadata_factorgeo <- metadata
# metadata_factorgeo$geo_type <- factor(metadata_factorgeo$geo_type, levels = c("county", "hrr", "msa", "dma", "state", "hhs", "nation"))
# auto_geo_list_by_signal <- arrange(
#   metadata_factorgeo,
#   geo_type
# ) %>% 
#   group_by(
#     data_source,
#     signal
#   ) %>%
#   summarize(
#     geos_list = paste(geo_type, collapse = ", "),
#     .groups = "keep"
#   ) %>%
#   ungroup()

# # Tool: Are there any data sources where geos_list is different for different signal?
# different_geos_by_signal <- count(auto_geo_list_by_signal, data_source, geos_list, name = "n_signals")
# # different_geos_by_signal
# # which(duplicated(select(different_geos_by_signal, data_source)))

# # Keep most common geos_list for each data source.
# most_common_geos_list <- group_by(different_geos_by_signal, data_source) %>% 
#   slice_max(n_signals, with_ties = FALSE)
# # most_common_geos_list
# leftover_datasource_geos <- anti_join(different_geos_by_signal, most_common_geos_list)
# # leftover_datasource_geos
# leftover_signal_geos <- semi_join(auto_geo_list_by_signal, leftover_datasource_geos)
# # leftover_signal_geos

# These values are applied first. They are the default (most common) geos for each data source.
avail_geos <- c(
  "chng" = glue("county,hrr,msa,state,hhs,nation"),
  "covid-act-now" = glue("county,hrr,msa,state,hhs,nation"),
  "doctor-visits" = glue("county,hrr,msa,state,hhs,nation"),
  "dsew-cpr" = glue("county,msa,state,hhs,nation"),
  "fb-survey" = glue("county,hrr,msa,state,nation"),
  "ght" = glue("hrr,msa,dma,state"),
  "google-survey" = glue("county,hrr,msa,state"),
  "google-symptoms" = glue("county,hrr,msa,state,hhs,nation"),
  "hhs" = glue("state,hhs,nation"),
  "hospital-admissions" = glue("county,hrr,msa,state,hhs,nation"),
  "indicator-combination" = glue("county,hrr,msa,state,hhs,nation"),
  "jhu-csse" = glue("county,hrr,msa,state,hhs,nation"),
  "nchs-mortality" = glue("state,nation"),
  # Quidel non-flu signals
  "quidel" = glue("county,hrr,msa,state,hhs,nation"),
  "safegraph" = glue("county,hrr,msa,state,hhs,nation"),
  "usa-facts" = glue("county,hrr,msa,state,hhs,nation"),
  "youtube-survey" = "state"
)

# These are signal-specific geo lists. These are less common and are applied as a patch.
dsew_geos <- glue("state,hhs,nation")
fb_geos1 <- glue("county,state,nation")
fb_geos2 <- glue("county,msa,state,nation")
hosp_geos <- glue("county,hrr,msa,state")
combo_geos <- glue("county,msa,state")
quidel_geos <- glue("msa,state")
leftover_signal_geos_manual <- tibble::tribble(
  ~data_source, ~signal, ~geos_list,
  "chng", "7dav_inpatient_covid", "state",
  "chng", "7dav_outpatient_covid", "state",
  
  "dsew-cpr", "booster_doses_admin_7dav", dsew_geos,
  "dsew-cpr", "doses_admin_7dav", dsew_geos,
  "dsew-cpr", "people_booster_doses", dsew_geos,
  
  "fb-survey", "smoothed_vaccine_barrier_appointment_location_tried", fb_geos1,
  "fb-survey", "smoothed_vaccine_barrier_other_tried", fb_geos1,
  "fb-survey", "smoothed_wvaccine_barrier_appointment_location_tried", fb_geos1,
  "fb-survey", "smoothed_wvaccine_barrier_other_tried", fb_geos1,
  
  "fb-survey", "smoothed_vaccine_barrier_appointment_time_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_childcare_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_document_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_eligible_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_language_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_no_appointments_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_none_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_technical_difficulties_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_technology_access_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_time_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_travel_tried", fb_geos2,
  "fb-survey", "smoothed_vaccine_barrier_type_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_appointment_time_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_childcare_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_document_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_eligible_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_language_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_no_appointments_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_none_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_technical_difficulties_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_technology_access_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_time_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_travel_tried", fb_geos2,
  "fb-survey", "smoothed_wvaccine_barrier_type_tried", fb_geos2,
  
  "hospital-admissions", "smoothed_adj_covid19", hosp_geos,
  "hospital-admissions", "smoothed_covid19", hosp_geos,
  
  "indicator-combination", "nmf_day_doc_fbc_fbs_ght", combo_geos,
  "indicator-combination", "nmf_day_doc_fbs_ght", combo_geos,
  
  # Quidel flu signals
  "quidel", "raw_pct_negative", quidel_geos,
  "quidel", "smoothed_pct_negative", quidel_geos,
  "quidel", "raw_tests_per_device", quidel_geos,
  "quidel", "smoothed_tests_per_device", quidel_geos
)

source_updated[, col] <- coalesce(avail_geos[source_updated$data_source], source_updated[[col]])

source_updated <- left_join(
  source_updated, leftover_signal_geos_manual,
  by = c("Signal" = "signal", "data_source")
) %>%
  mutate(`Available Geography` = coalesce(geos_list, `Available Geography`)) %>%
  select(-geos_list)


col <- "Delphi-Aggregated Geography"
# List available geo-levels that were created by Delphi (as opposed to being
# ingested directly from the data source), e.g. if available at the county,
# state, and nation levels but state and nation were aggregated by us from
# provided county data:  state,nation

# These values are applied first. They are the default (most common) geos for each data source.
avail_geos <- c(
  "chng" = glue("hrr,msa,state,hhs,nation"),
  "covid-act-now" = glue("hrr,msa,state,hhs,nation"),
  "doctor-visits" = glue("hrr,msa,state,hhs,nation"),
  "dsew-cpr" = glue("nation"),
  "fb-survey" = glue("county,hrr,msa,state,nation"),
  "ght" = glue("hrr,msa"),
  "google-survey" = glue("county,hrr,msa,state"),
  "google-symptoms" = glue("hrr,msa,hhs,nation"),
  "hhs" = glue("hhs,nation"),
  "hospital-admissions" = glue("county,hrr,msa,state,hhs,nation"),
  "indicator-combination" = glue("county,hrr,msa,state,hhs,nation"),
  "jhu-csse" = glue("hrr,msa,state,hhs,nation"),
  "nchs-mortality" = NA_character_,
  # Quidel non-flu signals
  "quidel" = glue("county,hrr,msa,state,hhs,nation"),
  "safegraph" = glue("county,hrr,msa,state,hhs,nation"),
  "usa-facts" = glue("hrr,msa,state,hhs,nation"),
  "youtube-survey" = "state"
)



# Save updated signals table to CSV [readr::write_csv]
write_csv(source_updated, file = "updated_signal_spreadsheet.csv")


# Final manual steps:
# open CSV in a GUI editor (excel or google sheets). copy scope date columns and paste into original spreadsheet online [manual]
