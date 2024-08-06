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
  library(purrr)
})

options(warn = 1)



# read in "Other Endpoints Signals" table as csv
#   source subdivision is in "source_sub" col
#   data signal is in "signal" col
#   start date is in "temp_start" col
#   end date is in "temp_end" col
signal_sheet <- suppressMessages(read_csv("delphi-eng-covidcast-data-sources-signals_-_Other_Endpoint_Signals.csv", na = c("", "NA", " ", "NaN"))) %>%
  # Drop empty rows
  filter(!is.na(`Source Subdivision`) ) #& !is.na(Signal)) # `Signal` makes extra certain data is missing


# read in "Other Endpoints Data Sources" table as csv
# shows how real data source names map to "source subdivisions"
#   data source is in "DB Source" col
#   source subdivision is in "source_sub" col
source_map <- suppressMessages(read_csv("delphi-eng-covidcast-data-sources-signals_-_Other_Endpoint_Data_Sources.csv", na = c("", "NA", " ", "NaN"))) %>%
  # Drop empty rows
  filter(!is.na(`Source Subdivision`))

dmytro_analysis <- suppressMessages(read_csv("delphi-prod-analysis-endpoint-status.csv", na = c("", "NA", " ", "NaN"))) %>% 
  rename(`Source Subdivision` = Endpoint) %>% 
  select(-Name)


signal_sheet <- bind_rows(
  signal_sheet,
  tibble::tribble(
    ~`Source Subdivision`, ~Signal, ~`Short Description`, ~`Include in signal discovery app`,
    
    "cdc", "location", "Two character state/territory code where the data was collected (51 states, including DC)", FALSE,
    "cdc", "epiweek", "The epiweek (YYYY-MM-DD) during which the data was collected", FALSE,
    "cdc", "num1", "Hits for pages like '%What You Should Know for the % Influenza Season%'", TRUE,
    "cdc", "num2", "Hits for pages like '%What To Do If You Get Sick%'", TRUE,
    "cdc", "num3", "Hits for pages like '%Flu Symptoms & Severity%'", TRUE,
    "cdc", "num4", "Hits for pages like '%How Flu Spreads%'", TRUE,
    "cdc", "num5", "Hits for pages like '%What You Should Know About Flu Antiviral Drugs%'", TRUE,
    "cdc", "num6", "Hits for pages like '%Weekly US Map%'", TRUE,
    "cdc", "num7", "Hits for pages like '%Basics%'", TRUE,
    "cdc", "num8", "Hits for pages like '%Flu Activity & Surveillance%'", TRUE,
    "cdc", "total", "Total number of hits for all CDC pages", TRUE,
    "cdc", "value", "", FALSE,
    
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
    "covid_hosp_facility", "state", "The two character state/territory code for the hospital.", FALSE,
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
    
    "delphi", "epiweek", "", FALSE,
    "delphi", "system", "", FALSE,
    "delphi", "forecast", "Forecast output as dataframe", FALSE,
    
    "dengue_nowcast", "location", "Two character state/territory code", FALSE,
    "dengue_nowcast", "epiweek", "The epiweek (YYYY-MM-DD) associated with the data", FALSE,
    "dengue_nowcast", "value", "Dengue fever nowcast", TRUE,
    "dengue_nowcast", "std", "Standard deviation associated with the nowcast", FALSE,
    
    "dengue_sensors", "name", "Abbreviation of sensor name. Some correspond to other data sources Delphi publishes. No auth token required to access: `sar3`, `epic`, `arch`. Auth token required to access: `twtr`, `gft`, `ght`, `ghtj`, `cdc`, `quid`, `wiki`.", FALSE,
    "dengue_sensors", "location", "Two character ISO 3166-1 alpha2 country code", FALSE,
    "dengue_sensors", "epiweek", "The epiweek (YYYY-MM-DD) associated with the data", FALSE,
    "dengue_sensors", "value", "Sensorized value", TRUE,
    
    "ecdc_ili", "release_date", "The date when this record was first published by the European CDC", FALSE,
    "ecdc_ili", "region", "Full English name of the European country", FALSE,
    "ecdc_ili", "issue", "The epiweek of publication (e.g. issue 201453 includes epiweeks up to and including 2014w53, but not 2015w01 or following)", FALSE,
    "ecdc_ili", "epiweek", "The epiweek during which the data was collected", FALSE,
    "ecdc_ili", "lag", "Number of weeks between `epiweek` and `issue`", FALSE,
    "ecdc_ili", "incidence_rate", "Number of ILI per 100k population", TRUE,
    
    "flusurv", "release_date", "The date when this record was first published by the CDC", FALSE,
    "flusurv", "issue", "The epiweek of publication (e.g. issue 201453 includes epiweeks up to and including 2014w53, but not 2015w01 or following)", FALSE,
    "flusurv", "epiweek", "The epiweek during which the data was collected", FALSE,
    "flusurv", "location", "The name of the catchment area (e.g. 'network_all', 'CA', 'NY_albany')", FALSE,
    "flusurv", "lag", "Number of weeks between `epiweek` and `issue`", FALSE,
    "flusurv", "rate_age_0", "Percent of hospitalizations that are associated with influenza for ages 0-4", TRUE,
    "flusurv", "rate_age_1", "Percent of hospitalizations that are associated with influenza for ages 5-17", TRUE,
    "flusurv", "rate_age_2", "Percent of hospitalizations that are associated with influenza for ages 18-49", TRUE,
    "flusurv", "rate_age_3", "Percent of hospitalizations that are associated with influenza for ages 50-64", TRUE,
    "flusurv", "rate_age_4", "Percent of hospitalizations that are associated with influenza for ages 65+", TRUE,
    "flusurv", "rate_age_5", "Percent of hospitalizations that are associated with influenza for ages 65-74", TRUE,
    "flusurv", "rate_age_6", "Percent of hospitalizations that are associated with influenza for ages 75-84", TRUE,
    "flusurv", "rate_age_7", "Percent of hospitalizations that are associated with influenza for ages 85+", TRUE,
    "flusurv", "rate_overall", "Percent of hospitalizations that are associated with influenza for all age groups", TRUE,
    
    "fluview", "release_date", "The date when this record was first published by the CDC", FALSE,
    "fluview", "issue", "The epiweek of publication (e.g. issue 201453 includes epiweeks up to and including 2014w53, but not 2015w01 or following)", FALSE,
    "fluview", "epiweek", "The epiweek during which the data was collected", FALSE,
    "fluview", "region", "The name of the location (e.g. 'nat', 'hhs1', 'cen9', 'pa', 'jfk')", FALSE,
    "fluview", "lag", "Number of weeks between `epiweek` and `issue`", FALSE,
    "fluview", "num_ili", "The number of ILI cases", TRUE,
    "fluview", "num_patients", "The total number of patients", TRUE,
    "fluview", "num_providers", "The number of reporting healthcare providers", TRUE,
    "fluview", "wili", "Weighted percent ILI", TRUE,
    "fluview", "ili", "Unweighted percent ILI", TRUE,
    "fluview", "num_age_0", "Number of influenza cases in ages 0-4", TRUE,
    "fluview", "num_age_1", "Number of influenza cases in ages 5-24", TRUE,
    "fluview", "num_age_2", "Number of influenza cases in ages 25-64", TRUE,
    "fluview", "num_age_3", "Number of influenza cases in ages 25-49", TRUE,
    "fluview", "num_age_4", "Number of influenza cases in ages 50-64", TRUE,
    "fluview", "num_age_5", "Number of influenza cases in ages 65+", TRUE,
    
    "fluview_clinical", "release_date", "The date when this record was first published by the CDC", FALSE,
    "fluview_clinical", "issue", "The epiweek of publication (e.g. issue 201453 includes epiweeks up to and including 2014w53, but not 2015w01 or following)", FALSE,
    "fluview_clinical", "epiweek", "The epiweek during which the data was collected", FALSE,
    "fluview_clinical", "region", "The name of the location (e.g. 'nat', 'hhs1', 'cen9', 'pa', 'jfk')", FALSE,
    "fluview_clinical", "lag", "Number of weeks between `epiweek` and `issue`", FALSE,
    "fluview_clinical", "total_specimens", NA_character_, TRUE,
    "fluview_clinical", "total_a", NA_character_, TRUE,
    "fluview_clinical", "total_b", NA_character_, TRUE,
    "fluview_clinical", "percent_positive", NA_character_, TRUE,
    "fluview_clinical", "percent_a", NA_character_, TRUE,
    "fluview_clinical", "percent_b", NA_character_, TRUE,
    
    "fluview_meta", "latest_update", "Date of latest update to `fluview` data", FALSE,
    "fluview_meta", "latest_issue", "Latest issue date saved to `fluview` data", FALSE,
    "fluview_meta", "table_rows", "Number of database rows in `fluview` data", FALSE,
    
    "gft", "location", "The name of the location", FALSE,
    "gft", "epiweek", "The epiweek (YYYY-MM-DD) associated with the data", FALSE,
    "gft", "num", "Flu search activity based on aggregated Google Search query data, standardized to make data more comparable across regions. The 'baseline' level for each region (shown as 0) is its average flu search activity, measured over many seasons. Activity levels for each region represent how much flu search activity differs from that region’s 'baseline' level.", TRUE,
    
    "ght", "query", "A search string or topic ID (see https://www.freebase.com/)", FALSE,
    "ght", "location", "Two-letter U.S. state abbreviation, or 'US' for entire US", FALSE,
    "ght", "epiweek", "The epiweek during which the queries were executed", FALSE,
    "ght", "value", "Relative search volume; the exact definition is still unclear", TRUE,
    
    "kcdc_ili", "release_date", "The date when this record was first published by the Korean CDC", FALSE,
    "kcdc_ili", "issue", "The epiweek of publication (e.g. issue 201453 includes epiweeks up to and including 2014w53, but not 2015w01 or following)", FALSE,
    "kcdc_ili", "epiweek", "The epiweek during which the data was collected", FALSE,
    "kcdc_ili", "lag", "Number of weeks between `epiweek` and `issue`", FALSE,
    "kcdc_ili", "region", "The name of the location (e.g. 'rok')", FALSE,
    "kcdc_ili", "ili", "Unweighted percent ILI", TRUE,
    
    
    
    
    "nowcast", "location", "Two character state/territory code", FALSE,
    "nowcast", "epiweek", "The epiweek (YYYY-MM-DD) associated with the data", FALSE,
    "nowcast", "value", "Nowcast", TRUE,
    "nowcast", "std", "Standard deviation associated with the nowcast", FALSE,
    

    
    
    
    
  )
)


output <- left_join(
  signal_sheet,
  source_map,
  by = "Source Subdivision",
  suffix = c("", "_source")
) %>% 
  left_join(
    dmytro_analysis,
    by = "Source Subdivision",
    suffix = c("", "_dmytro")
  )


output$Active <- output$Active_dmytro
output$Description <- output$`Short Description`
output$`Source Name` <- output$`External Name`
output$`Geographic Scope` <- output$Geos

output$`Delphi-Aggregated Geography` <- NA_character_


output$`Temporal Scope End` <- case_when(
  startsWith(output$`Source Subdivision`, "covid_hosp_") ~ "Ongoing",
  startsWith(output$`Source Subdivision`, "fluview") ~ "Ongoing"
)


output$`Who may access this signal?` <- case_when(
  output$`Public/Private` == "public" ~ "public",
  output$`Public/Private` == "Delphi" ~ "private"
)
output$`Who may be told about this signal?` <- output$`Who may access this signal?`
output$License <- output$License_source
output$Link <- output$Link_source


# c(
#   "cdc" = "",
#   "covid_hosp_facility_lookup" = "",
#   "covid_hosp_facility" = "",
#   "covid_hosp_state_timeseries" = "",
#   "delphi" = "",
#   "dengue_nowcast" = "",
#   "dengue_sensors" = NA_character_,
#   "ecdc_ili" = NA_character_,
#   "flusurv" = NA_character_,
#   "fluview_clinical" = NA_character_,
#   "fluview_meta" = NA_character_,
#   "fluview" = NA_character_,
#   "gft" = NA_character_,
#   "ght" = NA_character_,
#   "kcdc_ili" = NA_character_,
#   "meta_norostat" = NA_character_,
#   "meta" = NA_character_,
#   "nidss_dengue" = NA_character_,
#   "nidss_flu" = NA_character_,
#   "norostat" = NA_character_,
#   "nowcast" = "",
#   "paho_dengue" = NA_character_,
#   "quidel" = NA_character_,
#   "sensors" = NA_character_,
#   "twitter" = NA_character_,
#   "wiki" = NA_character_
# )





col <- "Available Geography"
values <- c(
  "cdc" = "state",
  "covid_hosp_facility_lookup" = "facility",
  "covid_hosp_facility" = "facility",
  "covid_hosp_state_timeseries" = "state",
  "delphi" = "hhs",
  "dengue_nowcast" = "state,nation",
  "dengue_sensors" = NA_character_,
  "ecdc_ili" = NA_character_,
  "flusurv" = NA_character_,
  "fluview_clinical" = NA_character_,
  "fluview_meta" = NA_character_,
  "fluview" = NA_character_,
  "gft" = NA_character_,
  "ght" = NA_character_,
  "kcdc_ili" = NA_character_,
  "meta_norostat" = NA_character_,
  "meta" = NA_character_,
  "nidss_dengue" = NA_character_,
  "nidss_flu" = NA_character_,
  "norostat" = NA_character_,
  "nowcast" = "state",
  "paho_dengue" = NA_character_,
  "quidel" = NA_character_,
  "sensors" = NA_character_,
  "twitter" = NA_character_,
  "wiki" = NA_character_
)

output[, col] <- values[output$`Source Subdivision`]


col <- "Time Type"
values <- c(
  "cdc" = "week",
  "covid_hosp_facility_lookup" = NA_character_,
  "covid_hosp_facility" = "week",
  "covid_hosp_state_timeseries" = "day",
  "delphi" = "week",
  "dengue_nowcast" = "week",
  "dengue_sensors" = NA_character_,
  "ecdc_ili" = NA_character_,
  "flusurv" = NA_character_,
  "fluview_clinical" = NA_character_,
  "fluview_meta" = NA_character_,
  "fluview" = NA_character_,
  "gft" = NA_character_,
  "ght" = NA_character_,
  "kcdc_ili" = NA_character_,
  "meta_norostat" = NA_character_,
  "meta" = NA_character_,
  "nidss_dengue" = NA_character_,
  "nidss_flu" = NA_character_,
  "norostat" = NA_character_,
  "nowcast" = "week",
  "paho_dengue" = NA_character_,
  "quidel" = NA_character_,
  "sensors" = NA_character_,
  "twitter" = NA_character_,
  "wiki" = NA_character_
)

output[, col] <- values[output$`Source Subdivision`]



col <- "Pathogen/\r\nDisease Area"
# covid,flu,rsv,pneumonia,dengue,norovirus
values <- c(
  "cdc" = NA_character_,
  "covid_hosp_facility_lookup" = NA_character_,
  "covid_hosp_facility" = NA_character_,
  "covid_hosp_state_timeseries" = NA_character_,
  "delphi" = NA_character_,
  "dengue_nowcast" = "dengue",
  "dengue_sensors" = "dengue",
  "ecdc_ili" = "flu",
  "flusurv" = "flu",
  "fluview_clinical" = "flu",
  "fluview_meta" = "flu",
  "fluview" = "flu",
  "gft" = NA_character_,
  "ght" = NA_character_,
  "kcdc_ili" = "flu",
  "meta_norostat" = "norovirus",
  "meta" = NA_character_,
  "nidss_dengue" = "dengue",
  "nidss_flu" = "flu",
  "norostat" = "norovirus",
  "nowcast" = NA_character_,
  "paho_dengue" = "dengue",
  "quidel" = NA_character_,
  "sensors" = NA_character_,
  "twitter" = NA_character_,
  "wiki" = NA_character_
)
output[, col] <- values[output$`Source Subdivision`]

flu_filter <- grepl("flu", output$Signal, ignore.case = TRUE) |
  grepl("flu", output$Description, ignore.case = TRUE)
covid_filter <- grepl("covid", output$Signal, ignore.case = TRUE) |
  grepl("covid", output$Description, ignore.case = TRUE)
dengue_filter <- grepl("dengue", output$Signal, ignore.case = TRUE) |
  grepl("dengue", output$Description, ignore.case = TRUE)
norovirus_filter <- grepl("noro", output$Signal, ignore.case = TRUE) |
  grepl("noro", output$Description, ignore.case = TRUE)
rsv_filter <- grepl("rsv", output$Signal, ignore.case = TRUE) |
  grepl("rsv", output$Description, ignore.case = TRUE)
output[, col] <- case_when(
  !is.na(output[, col, drop = TRUE]) ~ output[, col, drop = TRUE],
  map_lgl(output$Signal, ~ any(.x == c("location", "state", "epiweek", "date"))) ~ NA_character_,
  flu_filter & !covid_filter & !dengue_filter & !rsv_filter ~ "flu",
  !flu_filter & covid_filter & !dengue_filter & !rsv_filter ~ "covid",
  !flu_filter & !covid_filter & dengue_filter & !rsv_filter ~ "dengue",
  !flu_filter & !covid_filter & !dengue_filter & rsv_filter ~ "rsv",
  output$`Source Subdivision` == "gft" ~ "flu"
)


col <- "Signal Type"
hosp_filter <- grepl("hospitalized", output$Signal, ignore.case = TRUE) |
  grepl("hospitalized", output$Description, ignore.case = TRUE) |
  grepl("admission", output$Signal, ignore.case = TRUE) |
  grepl("admission", output$Description, ignore.case = TRUE)
test_filter <- grepl("test", output$Signal, ignore.case = TRUE) |
  grepl("test", output$Description, ignore.case = TRUE)
vaccine_filter <- grepl("vaccin", output$Signal, ignore.case = TRUE) |
  grepl("vaccin", output$Description, ignore.case = TRUE)
output[, col] <- case_when(
  !is.na(output[, col, drop = TRUE]) ~ output[, col, drop = TRUE],
  hosp_filter ~ "Hospitalizations",
  test_filter ~ "Testing",
  vaccine_filter ~ "Vaccines"
)

col <- "Severity Pyramid Rungs"
icu_filter <- grepl("icu", output$Signal, ignore.case = TRUE) |
  grepl("icu", output$Description, ignore.case = TRUE)
output[, col] <- case_when(
  !is.na(output[, col, drop = TRUE]) ~ output[, col, drop = TRUE],
  hosp_filter ~ "hospitalized",
  test_filter ~ "ascertained (case)",
  vaccine_filter ~ "population",
  icu_filter ~ "icu"
)


# Save updated signals table to CSV [readr::write_csv]
write_csv(output[, names(signal_sheet)], file = "updated_signal_spreadsheet.csv", na = "")


# Final manual steps:
# open CSV in a GUI editor (excel or google sheets). copy scope date columns and paste into original spreadsheet online [manual]
