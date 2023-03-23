#!/usr/bin/env Rscript

# disgusting hack to set up cwd
initial_options <- commandArgs(trailingOnly = FALSE)
file_arg_name <- "--file="
basename <- dirname(sub(file_arg_name, "", initial_options[grep(file_arg_name, initial_options)]))
setwd(basename)

options(epidata.url="http://delphi_web_epidata/epidata/")
source("../../src/client/delphi_epidata.R")

out <- function(res) {
  cat(paste(res$result, res$message, length(res$epidata), "\n"))
}

check <- function(res, exp_result, exp_message, exp_length) {
  stopifnot(res$result == exp_result)
  stopifnot(res$message == exp_message)
  stopifnot(length(res$epidata) == exp_length)
}

call_region_epiweeks <- function(fn_name) {
  fn <- Epidata[[fn_name]]
  cat(paste(fn_name,"\n"))
  fn(list('nat'), list(201440))
}

cat("server_version\n")
res <- Epidata$server_version()
stopifnot("version" %in% names(res))
cat("fluview\n")
res <- Epidata$fluview(list('nat'), list(201440, Epidata$range(201501, 201510)), auth="test")
check(res, -2, "no results", 0)
cat("fluview_meta\n")
res <- Epidata$fluview_meta()
check(res, 1, "success", 1)
res <- call_region_epiweeks("fluview_clinical")
check(res, -2, "no results", 0)
res <- call_region_epiweeks("flusurv")
check(res, -2, "no results", 0)
res <- call_region_epiweeks("ecdc_ili")
check(res, -2, "no results", 0)
res <- call_region_epiweeks("kcdc_ili")
check(res, -2, "no results", 0)
res <- call_region_epiweeks("gft")
check(res, -2, "no results", 0)
#res <- Epidata$ght("abc", list("nat"), list(201440), "cough")
#check(res, -2, "no results", 0)
#res <- Epidata$twitter("abc", list("nat"), epiweeks=list(201440))
#check(res, -2, "no results", 0)
cat("wiki\n")
res <- Epidata$wiki(list("abc"), list(20141201))
check(res, -2, "no results", 0)
#res <- Epidata$cdc("abc", list(201440), list("nat"))
#check(res, -2, "no results", 0
#res <- Epidata$quidel("abc", list(201440), list("nat"))
#check(res, -2, "no results", 0)
#res <- Epidata$norostat("abc", "nat", list(201440))
#check(res, -2, "no results", 0)
#res <- Epidata$meta_norostat("abc")
#out(res)
res <- call_region_epiweeks("nidss.flu")
check(res, -2, "no results", 0)
res <- call_region_epiweeks("nidss.dengue")
check(res, -2, "no results", 0)
cat("delphi\n")
res <- Epidata$delphi("xyz", 201440)
check(res, -2, "no results", 0)
#res <- Epidata$sensors("abc", list("def"), list("nat"), list(201440))
#check(res, -2, "no results", 0)
#res <- Epidata$dengue_sensors("abc", list("def"), list("nat"), list(201440))
#check(res, -2, "no results", 0)
res <- call_region_epiweeks("nowcast")
check(res, -2, "no results", 0)

# Fails with database error:
#res <- call_region_epiweeks("dengue_nowcast")
#out(res)
#check(res, -2, "no results", 0)

cat("meta\n")
res <- Epidata$meta()
check(res, 1, "success", 1)
cat("covidcast\n")
res <- Epidata$covidcast("abc", "def", "day", "nation", list(20200401), "us")
check(res, -2, "no results", 0)
cat("covidcast_meta\n")
res <- Epidata$covidcast_meta()
check(res, 1, "success", 16)
cat("covid_hosp\n")
res <- Epidata$covid_hosp("pa", 20201201)
check(res, -2, "no results", 0)
cat("covid_hosp_facility\n")
res <- Epidata$covid_hosp_facility(list("abc"), list(202050))
check(res, -2, "no results", 0)
cat("covid_hosp_facility_lookup\n")
res <- Epidata$covid_hosp_facility_lookup("pa")
check(res, 1, "success", 1)


