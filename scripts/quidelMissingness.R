library(epidatr)
library(dplyr)

signals <- c(
  #"covid_ag_raw_pct_positive",                 #"county", "state"
  #"covid_ag_raw_pct_positive_age_0_4",         #"county", "state" 
  #"covid_ag_smoothed_pct_positive",            #"county", "state" 
  #"covid_ag_smoothed_pct_positive_age_0_4",    #"county", "state" 
  #"covid_ag_smoothed_pct_positive_age_18_49"   #"county", "state"
  #"covid_ag_smoothed_pct_positive_age_65plus"   #"county", "state"
  
  
  "covid_ag_raw_pct_positive",                 #"hrr", "msa", "hhs", "nation"
  "covid_ag_smoothed_pct_positive"             #"hrr", "msa", "hhs", "nation"
  
  #"raw_pct_negative",         #FLU
  #"raw_tests_per_device",     #FLU
  #"smoothed_pct_negative",    #FLU
  #"smoothed_tests_per_device" #FLU 
)
names(signals) <- signals
lapply(signals, function(signal) {
  source <- "quidel"
  signal <- signals
  geo_type <- "msa"       #"county", "state", "hrr", "msa", "hhs", "nation"
  time_type <- "day"
  
  print(signal)
  print(geo_type)
  
  epidata <- pub_covidcast(
    source,
    signal,
    geo_type = geo_type,
    geo_values = "*",
    time_type = time_type,
    time_values = c(
      "2021-03-01",
      "2021-03-02",
      "2021-03-03",
      "2021-03-04",
      "2021-03-05",
      "2021-03-06",
      "2021-03-07",
      "2021-03-08",
      "2021-03-09",
      "2021-03-10",
      "2021-03-11",
      "2021-03-12",
      "2021-03-13",
      "2021-03-14",
      "2021-03-15",
      "2021-03-16",
      "2021-03-17",
      "2021-03-18",
      "2021-03-19",
      "2021-03-20",
      "2021-03-21",
      "2021-03-22",
      "2021-03-23",
      "2021-03-24",
      "2021-03-25",
      "2021-03-26",
      "2021-03-27",
      "2021-03-28",
      "2021-03-29",
      "2021-03-30"
    )
  )
  
  # Number of locations reported for each reference date
  count_geos_by_date <- count(epidata, time_value)
  # print(count_geos_by_date)
  print(max(count_geos_by_date$n) / 3143 * 100)
  print(mean(count_geos_by_date$n) / 3143 * 100)
  
  return(max(count_geos_by_date$n) / 3143 * 100)
  
})

####################################### geo_type = "county"
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "county"
# [1] 76.32835
# [1] 72.70973
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "county"
# [1] 76.32835
# [1] 72.70973
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "county"
# [1] 76.32835
# [1] 72.70973
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "county"
# [1] 76.32835
# [1] 72.70973
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "county"
# [1] 76.32835
# [1] 72.70973
# $covid_ag_raw_pct_positive
# [1] 76.32835
# 
# $covid_ag_raw_pct_positive_age_0_4
# [1] 76.32835
# 
# $covid_ag_smoothed_pct_positive
# [1] 76.32835
# 
# $covid_ag_smoothed_pct_positive_age_0_4
# [1] 76.32835
# 
# $covid_ag_smoothed_pct_positive_age_18_49
# [1] 76.32835



####################################### geo_type = "state"
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "state"
# [1] 6.04518
# [1] 5.738679
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "state"
# [1] 6.04518
# [1] 5.738679
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "state"
# [1] 6.04518
# [1] 5.738679
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "state"
# [1] 6.04518
# [1] 5.738679
# covid_ag_raw_pct_positive 
# "covid_ag_raw_pct_positive" 
# covid_ag_raw_pct_positive_age_0_4 
# "covid_ag_raw_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive 
# "covid_ag_smoothed_pct_positive" 
# covid_ag_smoothed_pct_positive_age_0_4 
# "covid_ag_smoothed_pct_positive_age_0_4" 
# covid_ag_smoothed_pct_positive_age_18_49 
# "covid_ag_smoothed_pct_positive_age_18_49" 
# [1] "state"
# [1] 6.04518
# [1] 5.738679
# $covid_ag_raw_pct_positive
# [1] 6.04518
# 
# $covid_ag_raw_pct_positive_age_0_4
# [1] 6.04518
# 
# $covid_ag_smoothed_pct_positive
# [1] 6.04518
# 
# $covid_ag_smoothed_pct_positive_age_0_4
# [1] 6.04518
# 
# $covid_ag_smoothed_pct_positive_age_18_49
# [1] 6.04518

####################################### geo_type = "state"

