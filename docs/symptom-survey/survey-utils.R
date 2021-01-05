library(readr)
library(purrr)
library(dplyr)

#' Fetch all survey data in a chosen directory.
#'
#' There can be multiple data files for a single day of survey responses, for
#' example if the data is reissued when late-arriving surveys are recorded. Each
#' file contains *all* data recorded for that date, so only the most recently
#' updated file for each date is needed.
#'
#' This function extracts the date from each file, determines which files
#' contain reissued data, and produces a single data frame representing the most
#' recent data available for each day. It can read gzip-compressed CSV files,
#' such as those on the SFTP site, using `readr::read_csv`.
#'
#' This function handles column types correctly for surveys up to Wave 4.
#'
#' @param directory Directory in which to look for survey CSV files, relative to
#'   the current working directory.
#' @param pattern Regular expression indicating which files in that directory to
#'   open. By default, selects all `.csv.gz` files, such as those downloaded
#'   from the SFTP site.
#' @return A single data frame containing all survey responses. Note that this
#'   data frame may have millions of rows and use gigabytes of memory, if this
#'   function is run on *all* survey responses.
get_survey_df <- function(directory, pattern = "*.csv.gz$") {
  files <- list.files(directory, pattern = pattern)

  files <- map_dfr(files, get_file_properties)

  latest_files <- files %>%
    group_by(date) %>%
    filter(recorded == max(recorded)) %>%
    ungroup() %>%
    pull(filename)

  big_df <- map_dfr(
    latest_files,
    function(f) {
      # stop readr from thinking commas = thousand separators,
      # and from inferring column types incorrectly
      read_csv(file.path(directory, f), locale = locale(grouping_mark = ""),
               col_types = cols(
                 A2b = col_number(),
                 A3 = col_character(),
                 A4 = col_number(),
                 B2 = col_character(),
                 B2_14_TEXT = col_character(),
                 B2c = col_character(),
                 B2c_14_TEXT = col_character(),
                 B4 = col_number(),
                 B5 = col_number(),
                 B7 = col_character(),
                 B10b = col_character(),
                 B12a = col_character(),
                 C1 = col_character(),
                 C3 = col_number(),
                 C4 = col_number(),
                 C5 = col_number(),
                 C7 = col_number(),
                 C13 = col_character(),
                 C13a = col_character(),
                 D1_4_TEXT = col_character(),
                 E3 = col_character(),
                 fips = col_character(),
                 UserLanguage = col_character(),
                 StartDatetime = col_character(),
                 EndDatetime = col_character(),
                 Q65 = col_integer(),
                 Q66 = col_integer(),
                 Q67 = col_integer(),
                 Q68 = col_integer(),
                 Q69 = col_integer(),
                 Q70 = col_integer(),
                 Q71 = col_integer(),
                 Q72 = col_integer(),
                 Q73 = col_integer(),
                 Q74 = col_integer(),
                 Q75 = col_integer(),
                 Q76 = col_integer(),
                 Q77 = col_integer(),
                 Q78 = col_integer(),
                 Q79 = col_integer(),
                 Q80 = col_integer(),
                 .default = col_number()))
    }
  )
  return(big_df)
}

## Helper function to extract dates from each file's filename.
get_file_properties <- function(filename) {
  short <- strsplit(filename, ".", fixed = TRUE)[[1]][1]
  parts <- strsplit(short, "_", fixed = TRUE)[[1]]

  filedate <- as.Date(paste(parts[3:5], collapse = "-"))
  recordeddate <- as.Date(paste(parts[7:9], collapse = "-"))

  return(data.frame(filename = filename,
                    date = filedate,
                    recorded = recordeddate))
}
