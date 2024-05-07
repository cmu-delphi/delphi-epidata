# Load packages
suppressPackageStartupMessages({
  library(epidatr) # Access Delphi API
  library(dplyr) # Data handling
  library(readr) # Import csv sheet
  library(pipeR) # special pipe %>>%
  library(glue) # f-string formatting
})

options(warn = 1)


# COVIDcast metadata
# Metadata documentation: https://cmu-delphi.github.io/delphi-epidata/api/covidcast_meta.html

metadata <- pub_covidcast_meta()
# Convert `last_update` into a datetime.
# metadata$last_update <- as.POSIXct(metadata$last_update, origin = "1970-01-01")
## If don't want the hours, etc, truncate with `as.Date`
metadata$last_update <- as.Date(as.POSIXct(metadata$last_update, origin = "1970-01-01"))


#Patch NCHS-mortality max_time data into metadata, and min_time
source_name = "nchs-mortality"  #optional to use this variable
nchs_row_nums = which(metadata$data_source == source_name)

metadata$min_time <- as.character(metadata$min_time)
metadata$max_time <- as.character(metadata$max_time)
metadata$max_issue <- as.character(metadata$max_issue)

for (index in nchs_row_nums) {
  row = metadata[index, ]
    epidata <- pub_covidcast(   # epidata is corresponding data set, ie) all counties and dates between min max
    source = source_name,
    signals = row$signal,
    time_type = as.character(row$time_type),
    geo_type = as.character(row$geo_type),
    geo_values = "*",
    time_values = epirange(199001, 203001)
  )
  column = epidata$time_value   #col variable is optional, helps minimize typing
  metadata[index, "min_time"] = epidatr:::date_to_epiweek(min(column)) %>% 
    as.character() %>>%
    { paste0(substr(., 1, 4), "-", substr(., 5, 6)) }
  metadata[index, "max_time"] = epidatr:::date_to_epiweek(max(column)) %>% 
    as.character() %>>%
    { paste0(substr(., 1, 4), "-", substr(., 5, 6)) }
  metadata[index, "max_issue"] = epidatr:::date_to_epiweek(max(epidata$issue)) %>% 
    as.character() %>>%
    { paste0(substr(., 1, 4), "-", substr(., 5, 6)) }
}

# keep only unique rows [dplyr::distinct]
# only keeps listed columns....does select as well
metadata_subset <- distinct(
  metadata,
  data_source,
  signal,
  min_time,
  max_time
)

# check that geo_types for a given signal have the same start/end dates
# counts number of rows with unique data_source-signal combination [base::anyDuplicated] for duplicates
# warning [stop] will indicate manual correction is required

if (anyDuplicated(select(metadata_subset, data_source, signal)) != 0){
  warning(
    "discovered geos for the same signal with different metadata values. ",
    "Currently, we are keeping the earliest min_time and the lastest max_time. ",
    "We also create a note column where dates differ by geo and list all geos ",
    "and all scope start/end dates"
  )
}

metadata_subset <- group_by(
  metadata,
  data_source,
  signal
) %>%
  summarize(
    min_time_notes = paste0("Start dates vary by geo: ", paste(geo_type, min_time, collapse = ", ")),
    n_unique_min_time = length(unique(min_time)),
    min_time = min(min_time),
    max_time_notes = paste0("End dates vary by geo: ", paste(geo_type, max_time, collapse = ", ")),
    n_unique_max_time = length(unique(max_time)),
    max_time = max(max_time),
    .groups = "keep"
  ) %>%
  ungroup()

metadata_subset[metadata_subset$n_unique_min_time <= 1, "min_time_notes"] <- NA_character_
metadata_subset[metadata_subset$n_unique_max_time <= 1, "max_time_notes"] <- NA_character_


# read in SIGNALS table as csv from https://docs.google.com/spreadsheets/d/1zb7ItJzY5oq1n-2xtvnPBiJu2L3AqmCKubrLkKJZVHs/edit#gid=329338228
#   source subdivision is in "source_sub" col
#   data signal is in "signal" col
#   start date is in "temp_start" col
#   end date is in "temp_end" col
signal_sheet <- suppressMessages(read_csv("delphi-eng-covidcast-data-sources-signals_Signals.csv")) %>%
  # Drop empty rows
  filter(!is.na(`Source Subdivision`) & !is.na(Signal)) # (Signa) makes extra certain data is missing

# Fields we want to add.
new_fields <- c(
  "Geographic Scope",
  "Temporal Scope Start",
  "Temporal Scope End",
  "Reporting Cadence",
  "Reporting Lag",
  "Revision Cadence",
  "Demographic Scope",
  "Demographic Disaggregation", ###Change to "Demographic Breakdowns" when granted sheet access
  "Severity Pyramid Rungs",
  "Data Censoring",
  "Missingness",
  "Who may Access this signal?",
  "Who may be told about this signal?",
  "Use Restrictions",
  "Link to DUA"
)
names(new_fields) <- new_fields

# Which ones have missing values and need to be filled in?
new_fields_with_missings <- lapply(new_fields, function(col) {
  any(is.na(signal_sheet[, col]))
})
new_fields_with_missings <- names(new_fields_with_missings[unlist(new_fields_with_missings)])

message(
  paste(new_fields_with_missings, collapse = ", "),
  " columns contain missing values and need to be filled in programmatically"
)


# read in SOURCES table as csv from https://docs.google.com/spreadsheets/d/1zb7ItJzY5oq1n-2xtvnPBiJu2L3AqmCKubrLkKJZVHs/edit#gid=0
# shows how real data source names map to "source subdivisions"
#   data source is in "DB Source" col
#   source subdivision is in "source_sub" col
source_map <- suppressMessages(read_csv("delphi-eng-covidcast-data-sources-signals_Sources.csv")) %>%
  # Drop empty rows
  filter(!is.na(`Source Subdivision`) & !is.na(`DB Source`)) %>%
  rename(data_source =`DB Source`) %>%
  select(data_source, "Source Subdivision")

# left join metadata_subset with source_map
source2 <- left_join(
  signal_sheet,
  source_map,
  by = "Source Subdivision"
)

# left join signal_sheet with source2
# result: table with source subdivision, signal, scope start, scope end, min date, max date
source3 <- left_join(
  source2,
  metadata_subset,
  by = c("Signal" = "signal", "data_source")
)

# select: source subdivision, signal, scope start, scope end, min_time, max_time
# first reformat max_time col to character for compatibility
# also convert min_time col to character (easier to move times over to google spreadsheet without corrupting)
# *only in dplyr can you use col names without quotations, as.character is base function
# *min_time, we can just use the earliest date available and not specify each geo's different dates
source4 <- mutate(
  source3,
  `Temporal Scope Start Note` = min_time_notes,
  `Temporal Scope End Note` = max_time_notes,
  max_time = as.character(max_time),
  min_time = as.character(min_time)
)


# overwrite scope start with min_time [dplyr::mutate]. Set all scope end values
# to "Ongoing" as default. Make copies of manually-filled in columns so we can
# compare our programmatic results.
source5 <- source4 %>%
  mutate(
    `Temporal Scope Start manual` = `Temporal Scope Start`,
    `Temporal Scope End manual` = `Temporal Scope End`,
    `Temporal Scope Start` = min_time,
    `Temporal Scope End` = max_time
  )


# Inactive data_sources list
inactive_sources <- c(
  "jhu-csse", "dsew-cpr", "fb-survey", "covid-act-now", "ght", "google-survey",
  "indicator-combination", "safegraph", "usa-facts"
)

# Inactive signals list, where some signals for a given data source are active
# and some are inactive.
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

if (filter(source55, data_source %in% inactive_sources) %>% pull(active) %>% any()) {
  stop("Some data sources that should be fully inactive list active signals",
       "Data handling above probably has a bug.")
}

# overwrite scope end with max_time where signal/data source is active [dplyr::mutate]
active_mask <- source55$active
source55$`Temporal Scope End`[active_mask] <- "Ongoing"


# delete helper columns (min and max_time, active) [dplyr::select]
source6 <- select(
  source55,
  -min_time,
  -max_time,
  -active
)

# # Check that our programmatically-derived and manually-filled temporal scope columns match
# compare_start_dates <- filter(source6, !is.na(`Temporal Scope Start manual`)) %>%
#   mutate(compare = `Temporal Scope Start manual` == `Temporal Scope Start`)
# if (!all(compare_start_dates$compare)) {
#   warning("Not all start dates match between programmatic and manual versions. ",
#           "See rows ", paste(which(!compare_start_dates$compare), collapse = ", "))
# } 
# # Examine the ones that don't match
# # These differences are acceptable
# source6[which(!compare_start_dates$compare), c("data_source", "Signal", "Temporal Scope Start manual", "Temporal Scope Start", "Temporal Scope Start Note")]

# compare_end_dates <- filter(source6, !is.na(`Temporal Scope End manual`)) %>%
#   mutate(compare = `Temporal Scope End manual` == `Temporal Scope End`)
# if (!all(compare_end_dates$compare)) {
#   warning("Not all end dates match between programmatic and manual versions. ",
#           "See rows ", paste(which(!compare_end_dates$compare), collapse = ", "))
# }
# # Examine the ones that don't match
# # These differences are acceptable
# source6[which(!compare_end_dates$compare), c("data_source", "Signal", "Temporal Scope End manual", "Temporal Scope End", "Temporal Scope End Note")]

# our new df MUST have the same row order as the signal spreadsheet
sort_order_is_the_same <- identical(
  select(source6, `Source Subdivision`, Signal),
  select(signal_sheet, `Source Subdivision`, Signal)
)

if (!sort_order_is_the_same) {
  stop("new signal fields are sorted differently than signal spreadsheet. ",
       "Columns cannot be pasted in as-is")
}

source_updated <- select(
  source6,
  -`Temporal Scope Start manual`,
  -`Temporal Scope End manual`,
  -min_time_notes,
  -max_time_notes,
  -n_unique_min_time,
  -n_unique_max_time
)



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
  "usa-facts" = "USA"
)
source_updated[, col] <- geo_scope[source_updated$data_source]


col <- "Available Geography"
# List all available geo-levels. If a geo-level was created by Delphi
# aggregation (as opposed to being ingested directly from the data source),
# indicate this as per this example:  county, state (by Delphi), National
# (by Delphi).

# Tool: Create lists of geos for each data source-signal combo based on what is reported in metadata (does not include quidel, at least with).
metadata_factorgeo <- metadata
metadata_factorgeo$geo_type <- factor(metadata_factorgeo$geo_type, levels = c("county", "hrr", "msa", "dma", "state", "hhs", "nation"))
auto_geo_list_by_signal <- arrange(
  metadata_factorgeo,
  geo_type
) %>% 
  group_by(
    data_source,
    signal
  ) %>%
  summarize(
    geos_list = paste(geo_type, collapse = ", "),
    .groups = "keep"
  ) %>%
  ungroup()

# Tool: Are there any data sources where geos_list is different for different signal?
different_geos_by_signal <- count(auto_geo_list_by_signal, data_source, geos_list, name = "n_signals")
different_geos_by_signal
# which(duplicated(select(different_geos_by_signal, data_source)))
# # [1]  2  6  8  9 15 17

# Keep most common geos_list for each data source.
most_common_geos_list <- group_by(different_geos_by_signal, data_source) %>% 
  slice_max(n_signals, with_ties = FALSE)
# most_common_geos_list
leftover_datasource_geos <- anti_join(different_geos_by_signal, most_common_geos_list)
# leftover_datasource_geos
leftover_signal_geos <- semi_join(auto_geo_list_by_signal, leftover_datasource_geos)
# leftover_signal_geos

delphi_agg_text <- " (by Delphi)"

# These values are applied first. They are the default (most common) geos for each data source.
avail_geos <- c(
  "chng" = glue("county, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "covid-act-now" = glue("county, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "doctor-visits" = glue("county, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "dsew-cpr" = glue("county, msa, state, hhs, nation{delphi_agg_text}"),
  "fb-survey" = glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, nation{delphi_agg_text}"),
  "ght" = glue("hrr{delphi_agg_text}, msa{delphi_agg_text}, dma, state"),
  "google-survey" = glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}"),
  "google-symptoms" = glue("county, hrr{delphi_agg_text}, msa{delphi_agg_text}, state, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "hhs" = glue("state, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "hospital-admissions" = glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "indicator-combination" = glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "jhu-csse" = glue("county, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "nchs-mortality" = glue("state, nation"),
  # TODO check against actual data. Or maybe there's an internal/private version of metadata that includes Quidel stats?
  "quidel" = glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "safegraph" = glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "usa-facts" = glue("county, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, hhs{delphi_agg_text}, nation{delphi_agg_text}"),
  "youtube-survey" = "state{delphi_agg_text}"
)

# These are signal-specific geo lists. These are less common and are applied as a patch.
dsew_geos <- glue("state, hhs, nation{delphi_agg_text}")
fb_geos1 <- glue("county{delphi_agg_text}, state{delphi_agg_text}, nation{delphi_agg_text}")
fb_geos2 <- glue("county{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}, nation{delphi_agg_text}")
hosp_geos <- glue("county{delphi_agg_text}, hrr{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}")
combo_geos <- glue("county{delphi_agg_text}, msa{delphi_agg_text}, state{delphi_agg_text}")
quidel_geos <- glue("msa{delphi_agg_text}, state{delphi_agg_text}")
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
  # TODO check against actual data. Or maybe there's an internal/private version of metadata that includes Quidel stats?
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


# Temporal Scope Start
# Above. YYYY-MM-DD, with epiweeks as YYYY-WW. Formatted as a string

# Temporal Scope End
# Above. YYYY-MM-DD, with epiweeks as YYYY-WW, or "Ongoing" if still ongoing.
# Formatted as a string


col <- "Reporting Cadence"
# E.g. daily, weekly, etc. Might not be the same as Temporal Granularity
avail_geos <- c(
  "chng" = "daily",
  "covid-act-now" = "daily",
  "doctor-visits" = "daily",
  "dsew-cpr" = "daily",
  "fb-survey" = "daily",
  "ght" = "daily",
  "google-survey" = "daily",
  "google-symptoms" = "daily",
  "hhs" = "weekly",
  "hospital-admissions" = "daily",
  "indicator-combination" = "daily",
  "jhu-csse" = "daily",
  "nchs-mortality" = "weekly",
  "quidel" = "daily",
  "safegraph" = "weekly",
  "usa-facts" = "weekly"
)

# TOOD to be renamed to "Typical Reporting Lag" @Carlyn
col <- "Typical Reporting Lag"
# The number of days as an unstructured field, e.g. "3-5 days", from the last
# day of a reported period until the first reported value for that period is
# usually available in Epidata. E.g. if reporting U.S. epiweeks
# (Sunday through Saturday), and the first report is usually available in
# Epidata on the following Friday, enter 6.
#
# By "usually available" we mean when it's "supposed to be" available based on
# our current understanding of the data provider's operations and Delphi's
# ingestion pipeline. That would be the date on which we think of the data
# as showing up "on time", and relative to which we will track unusual
# delays.
#
# values are from production params files, e.g.
# https://github.com/cmu-delphi/covidcast-indicators/blob/d36352b/ansible/templates/changehc-params-prod.json.j2#L42-L43,
# and sirCAL params
# https://github.com/cmu-delphi/covidcast-indicators/blob/main/ansible/templates/sir_complainsalot-params-prod.json.j2#L16

# Make a map between each data source (or source subdivision) and value. The
# value can be numeric, string, etc.
reporting_lag <- c(
  "chng" = "4-5 days",
  "covid-act-now" = "2-9 days",
  "doctor-visits" = "3-6 days",
  "dsew-cpr" = "3-9 days",
  "fb-survey" = "1 day",
  "ght" = "4-5 days",
  "google-survey" = "1-2 days",
  "google-symptoms" = "4-7 days",
  "hhs" = "5-11 days",
  "hospital-admissions" = "3-4 days",
  "indicator-combination" = "1-3 days",
  "jhu-csse" = "1 day",
  "nchs-mortality" = "11-17 days",
  "quidel" = "5-6 days",
  "safegraph" = "3-11 days",
  "usa-facts" = "2-8 days"
)
# Index (using `[]`) into the map using the data_source (or source division)
# column and save to the relevant field.
# Using the data_source to index into the map puts the output into the same
# order as the dataframe.
source_updated[, col] <- reporting_lag[source_updated$data_source]

# TOOD to be renamed to "Typical Revision Cadence" @Carlyn
col <- "Typical Revision Cadence"
# How frequently are revised values (AKA backfill) usually made available as
# an unstructured field, e.g. "Weekly (usually Fridays)", "daily", etc. If
# there are no reporting revisions, enter "None".
revision_cadence <- c(
  "chng" = "Daily. The source experiences heavy backfill with data delayed for a couple of weeks. We expect estimates available for the most recent 4-6 days to change substantially in later data revisions (having a median delta of 10% or more). Estimates for dates more than 45 days in the past are expected to remain fairly static (having a median delta of 1% or less), as most major revisions have already occurred.",
  "covid-act-now" = "Daily. Most recent test positivity rates do not change substantially (having a median delta of close to 0). However, most recent total tests performed are expected to increase in later data revisions (having a median increase of 7%). Values more than 5 days in the past are expected to remain fairly static (with total tests performed having a median increase of 1% of less), as most major revisions have already occurred.",
  "doctor-visits" = "Daily. The source experiences heavy backfill with data delayed for a couple of weeks. We expect estimates available for the most recent 5-7 days to change substantially in later data revisions (having a median delta of 10% or more). Estimates for dates more than 50 days in the past are expected to remain fairly static (having a median delta of 1% or less), as most major revisions have already occurred.",
  "dsew-cpr" = "Daily. This data source is susceptible to large corrections that can create strange data effects such as negative counts and sudden changes of 1M+ counts from one day to the next.",
  "fb-survey" = "Daily, for 5 consecutive issues for each report date",
  "ght" = "None",
  "google-survey" = "Daily, for 3 consecutive issues for each report date",
  "google-symptoms" = "None",
  "hhs" = "Monthly. Backfill is relatively uncommon in this dataset (80% of dates from November 1, 2020 onward are never touched after their first issue) and most such updates occur one to two weeks after information about a date is first published. In rare instances, a value may be updated 10 weeks or more after it is first published.",
  "hospital-admissions" = "Daily. The source experiences heavy backfill with data delayed for a couple of weeks. We expect estimates available for the most recent 7-13 days to change substantially in later data revisions (having a median delta of 10% or more). Estimates for dates more than 57 days in the past are expected to remain fairly static (having a median delta of 1% or less), as most major revisions have already occurred.",
  "indicator-combination" = "Daily",
  "jhu-csse" = "None. The raw data reports cumulative cases and deaths, which
     Delphi diffs to compute incidence. Raw cumulative figures are sometimes
     corrected by adjusting the reported value for a single day, but revisions
     do not affect past report dates.",
  "nchs-mortality" = "Weekly. All-cause mortality takes ~6 weeks on average to achieve 99% of its final value (https://link.springer.com/article/10.1057/s41271-021-00309-7)",
  "quidel" = NA_character_, # Happens, up to 6+ weeks after the report date. # TODO
  "safegraph" = "None",
  "usa-facts" = "None. The raw data reports cumulative cases and deaths, which Delphi diffs to compute incidence. Raw cumulative figures are sometimes corrected by adjusting the reported value for a single day, but revisions do not affect past report dates."
)
source_updated[, col] <- revision_cadence[source_updated$data_source]

col <- "Demographic Scope"
# The demographic group covered by the report.
# E.g. "all", "Pediatric", "Adult", "Women", "adult facebook
# users", "MSM", "Google search users", "VA Health system
# members", "smartphone users", …
demo_scope <- c(
  "chng" = "Nationwide Change Healthcare network",
  "covid-act-now" = "Hospital patients",
  "doctor-visits" = "Nationwide Optum network",
  "dsew-cpr" = "All",
  "fb-survey" = "Adult Facebook users",
  "ght" = "Google search users",
  "google-survey" = "Google ad publisher website, Google's Opinions Reward app, and similar application users",
  "google-symptoms" = "Google search users",
  "hhs" = "All",
  "hospital-admissions" = "Nationwide Optum network",
  "indicator-combination" = "This source is a combination of several signals representing different populations, and doesn't correspond to a single demographic group",
  "jhu-csse" = "All",
  "nchs-mortality" = "All",
  "quidel" = "Nationwide Quidel testing equipment network",
  "safegraph" = "Safegraph panel members who use mobile devices",
  "usa-facts" = "All"
)
source_updated[, col] <- demo_scope[source_updated$data_source]

# TODO rename to "Demographic Breakdowns" @Carlyn
col <- "Demographic Breakdowns"
# What demographic breakdowns are available, e.g. "by age groups 0-17,
# 18-64, 65+", "by race/ethnicity", "by gender".
#
# These might be used in filters, so the values need to be structured. E.g.
# it could be a list of all available breakdowns, e.g. "gender, race",
# or "age bands(0-17,18-64,65+)", or "None" if no breakdown. If it's easier,
# we can separate it into three different columns: "Gender Breakdown"
# (yes/no), "Race Breakdown" (yes/no), and "Age breakdown" (list of age
# bands, or "none")
demo_breakdowns <- c(
  "chng" = "None",
  "covid-act-now" = "None",
  "doctor-visits" = "None",
  "dsew-cpr" = "None",
  "fb-survey" = "None. However, contingency tables containing demographic breakdowns of survey data are available for download (https://cmu-delphi.github.io/delphi-epidata/symptom-survey/contingency-tables.html).",
  "ght" = "None",
  "google-survey" = "None",
  "google-symptoms" = "None",
  "hhs" = "None",
  "hospital-admissions" = "None",
  "indicator-combination" = "None",
  "jhu-csse" = "None",
  "nchs-mortality" = "None",
  "quidel" = "age (0-17, 0-4, 5-17, 18-49, 50-64, 65+)",
  "safegraph" = "None",
  "usa-facts" = "None"
)
source_updated[, col] <- demo_breakdowns[source_updated$data_source]
# Quidel covid has age bands, but quidel flu doesn't.
source_updated[source_update$`Source Subdivision` == "quidel-flu", col] <- "None"

# TODO name in spreadsheet ends with a space -- remove @Carlyn
col <- "Severity Pyramid Rungs"
# One or more rungs to which this signal best relates:
# https://docs.google.com/presentation/d/1K458kZsncwwjNMOnlkaqHA_0Vm7PEz6g43fYy4GII10/edit#slide=id.g10e023ed748_0_163


# TODO
col <- "Data Censoring"
# Has any of the data been censored (e.g. small counts)?
#
# TODO: If so how, and how much impact does it have (e.g. approximate fraction of
# counts affected).
#
# This is an unstructured text field.
data_censoring <- c(
  "chng" = "Discarded if over a given 7-day period an estimate is computed with 100 or fewer observations",
  "covid-act-now" = "Discarded if sample size (total tests performed) is 0. It is unknown what, if any, censoring the data source performs",
  "doctor-visits" = "Discarded if over a given 7-day period an estimate is computed with 500 or fewer observations",
  "dsew-cpr" = "It is unknown what, if any, censoring the data source performs",
  "fb-survey" = "Discarded if an estimate is based on fewer than 100 survey responses. For signals reported using a 7-day average (those beginning with 'smoothed_'), this means a geographic area must have at least 100 responses in 7 days to be reported.

  This affects some items more than others. For instance, some survey items are only asked of a subset of survey respondents. It also affects some geographic areas more than others, particularly rural areas with low population densities. When doing analysis of county-level data, one should be aware that missing counties are typically more rural and less populous than those present in the data, which may introduce bias into the analysis.",
  "ght" = NA_character_,
  "google-survey" = NA_character_,
  "google-symptoms" = "Unavailable when daily volume in a region does not meet quality or privacy thresholds, as set by Google. Google also uses differential privacy, which adds artificial noise to the raw datasets",
  "hhs" = NA_character_, # TODO
  "hospital-admissions" = "Discarded if over a given 7-day period an estimate is computed with 500 or fewer observations",
  "indicator-combination" = NA_character_,
  "jhu-csse" = NA_character_, # TODO
  "nchs-mortality" = "Unavailable by NCHS when counts are between 1 and 9, and for weeks where the counts are less than 50% of the expected number, since these provisional counts are highly incomplete and potentially misleading",
  "quidel" = "Discarded when an estimate is based on fewer than 50 tests. For smoothed signals at the county, MSA, and HRR levels with between 25 and 50 tests, the estimate is computed with the original N tests and 50-N synthetic tests that have the same test positivity rate as the parent state (state with the largest proportion of the population in this region); estimates are entirely discarded when based on fewer than 25 tests",
  "safegraph" = NA_character_,
  "usa-facts" = NA_character_
)
signal_specific_censoring <- tibble::tribble(
  ~data_source, ~signal, ~note,
  "dsew-cpr", "covid_naat_pct_positive_7dav", "Discarded when the 7dav NAAT test volume provided in the same originating
    spreadsheet, corresponding to a period ~4 days earlier, is 5 or fewer. This removes 10-20% of counties (https://github.com/cmu-delphi/covidcast-indicators/issues/1513). It is unknown what, if any, censoring the data source performs",
)
source_updated[, col] <- data_censoring[source_updated$data_source]

# TODO
col <- "Missingness"
# How much missingness is there, and for what reasons? Is it possible to
# distinguish a missing value from a true zero? This is an unstructured text
# field.
#
# E.g. in a signal that's available at county level, how many of the US's
# 3000+ counties are usually reported on? Not filter-related, so can be
# unstructured text. The problem is that these numbers can change
# dramatically over time, as has happened e.g. for the Facebook survey. I'm
# not sure what to do. Maybe just summarize the current state, e.g. "85%
# counties available in mid 2020, then gradually declined to 8% of counties
# by April 2024", and leave it at that. We could occasionally update it.
missingness <- c(
  "chng" = NA_character_,
  "covid-act-now" = "A few counties, most notably in California, are not covered by this data source",
  "doctor-visits" = NA_character_,
  "dsew-cpr" = NA_character_,
  "fb-survey" = "A missing value indicates no valid data OR, for test positivity, that the value was censored due to small sample size (<= 5)",
  "ght" = NA_character_,
  "google-survey" = NA_character_,
  "google-symptoms" = NA_character_,
  "hhs" = NA_character_,
  "hospital-admissions" = NA_character_,
  "indicator-combination" = NA_character_,
  "jhu-csse" = NA_character_,
  "nchs-mortality" = NA_character_,
  "quidel" = NA_character_,
  "safegraph" = NA_character_,
  "usa-facts" = NA_character_
)
source_updated[, col] <- missingness[source_updated$data_source]


# TODO best guess, should check
# TODO fix capitalization in name @Carlyn
col <- "Who may access this signal?"
# Who has the right to access this signal?  E.g. "Delphi, CDC" or "Delphi,
# ACHD, PADOH", or "public". Separate different orgs by comma.
orgs_allowed_access <- c(
  "chng" = "public",
  "covid-act-now" = "public",
  "doctor-visits" = "public",
  "dsew-cpr" = "public",
  "fb-survey" = "public",
  "ght" = "public",
  "google-survey" = "public",
  "google-symptoms" = "public",
  "hhs" = "public",
  "hospital-admissions" = "public",
  "indicator-combination" = "public",
  "jhu-csse" = "public",
  "nchs-mortality" = "public",
  "quidel" = "Delphi",
  "safegraph" = "public",
  "usa-facts" = "public"
)
source_updated[, col] <- orgs_allowed_access[source_updated$data_source]

# TODO best guess, should check
col <- "Who may be told about this signal?"
orgs_allowed_know <- c(
  "chng" = "public",
  "covid-act-now" = "public",
  "doctor-visits" = "public",
  "dsew-cpr" = "public",
  "fb-survey" = "public",
  "ght" = "public",
  "google-survey" = "public",
  "google-symptoms" = "public",
  "hhs" = "public",
  "hospital-admissions" = "public",
  "indicator-combination" = "public",
  "jhu-csse" = "public",
  "nchs-mortality" = "public",
  "quidel" = "public",
  "safegraph" = "public",
  "usa-facts" = "public"
)
source_updated[, col] <- orgs_allowed_know[source_updated$data_source]


# TODO add column to spreadsheet @Carlyn
col <- "License"
license <- c(
  "chng" = "CC BY-NC",
  "covid-act-now" = "CC BY-NC",
  "doctor-visits" = "CC BY-NC",
  "dsew-cpr" = "Public Domain US Government (https://www.usa.gov/government-works)",
  "fb-survey" = "CC BY",
  "ght" = "Google Terms of Service (https://policies.google.com/terms)",
  "google-survey" = "CC BY",
  "google-symptoms" = "Google Terms of Service (https://policies.google.com/terms)",
  "hhs" = "Public Domain US Government (https://www.usa.gov/government-works)",
  "hospital-admissions" = "CC BY",
  "indicator-combination" = "CC BY",
  "jhu-csse" = "CC BY",
  "nchs-mortality" = "NCHS Data Use Agreement (https://www.cdc.gov/nchs/data_access/restrictions.htm)",
  "quidel" = "CC BY",
  "safegraph" = "CC BY",
  "usa-facts" = "CC BY"
)
source_updated[, col] <- license[source_updated$data_source]

# TODO
col <- "Use Restrictions"
# Any important DUA restrictions on use, publication, sharing, linkage, etc.?
use_restrictions <- c(
  "chng" = NA_character_,
  "covid-act-now" = NA_character_,
  "doctor-visits" = NA_character_,
  "dsew-cpr" = NA_character_,
  "fb-survey" = NA_character_,
  "ght" = NA_character_,
  "google-survey" = NA_character_,
  "google-symptoms" = NA_character_,
  "hhs" = NA_character_,
  "hospital-admissions" = NA_character_,
  "indicator-combination" = NA_character_,
  "jhu-csse" = NA_character_,
  "nchs-mortality" = NA_character_,
  "quidel" = NA_character_,
  "safegraph" = NA_character_,
  "usa-facts" = NA_character_
)
source_updated[, col] <- use_restrictions[source_updated$data_source]

# TODO
col <- "Link to DUA"
dua_link <- c(
  "chng" = "https://cmu.box.com/s/cto4to822zecr3oyq1kkk9xmzhtq9tl2",
  "covid-act-now" = NA_character_, # contract?
  "doctor-visits" = "https://cmu.box.com/s/l2tz6kmiws6jyty2azwb43poiepz0565",
  "dsew-cpr" = NA_character_,
  "fb-survey" = "https://cmu.box.com/s/qfxplcdrcn9retfzx4zniyugbd9h3bos",
  "ght" = NA_character_,
  "google-survey" = NA_character_, # contract?
  "google-symptoms" = NA_character_,
  "hhs" = NA_character_,
  "hospital-admissions" = "https://cmu.box.com/s/l2tz6kmiws6jyty2azwb43poiepz0565",
  "indicator-combination" = NA_character_,
  "jhu-csse" = NA_character_,
  "nchs-mortality" = NA_character_,
  "quidel" = NA_character_,
  "safegraph" = "https://cmu.box.com/s/m0p1wpet4vuvey7od83n70h0e97ky2kg",
  "usa-facts" = NA_character_,
  "youtube-survey" = NA_character_  # contract?
)
source_updated[, col] <- dua_link[source_updated$data_source]


source_updated

# TODO: save updated signals table to CSV [readr::read_csv]


# Final manual steps:
# open CSV in a GUI editor (excel or google sheets). copy scope date columns and paste into original spreadsheet online [manual]