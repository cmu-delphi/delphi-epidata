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
#' such as those on the SFTP site, using `readr::read_csv()`.
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
      # stop readr from thinking commas = thousand separators, and from
      # inferring column types incorrectly
      read_csv(file.path(directory, f),
               locale = locale(grouping_mark = ""),
               col_types = cols(
                 UserLanguage = col_character(),
                 StartDatetime = col_datetime(),
                 EndDatetime = col_datetime(),
                 weight = col_number(),
                 wave = col_integer(),
                 fips = col_character(),
                 A2 = col_number(),
                 A5_1 = col_number(),
                 A5_2 = col_number(),
                 A5_3 = col_number(),
                 A2b = col_number(),
                 A3 = col_character(),
                 A4 = col_number(),
                 B2b = col_number(),
                 .default = col_character()))
    }
  )
  return(big_df)
}

#' Split multiselect options into codable form
#'
#' Multiselect options are coded by Qualtrics as a comma-separated string of
#' selected options, like "1,14", or the empty string if no options are
#' selected. Split these into vectors of selected options, which can be queried
#' using `is_selected()`.
#'
#' @param column vector of selections, like c("1,4", "5", ...)
#' @return list of same length, each entry of which is a vector of selected
#'   options
split_options <- function(column) {
  return(strsplit(column, ",", fixed = TRUE))
}

#' Test if a specific choice is selected in a multiselect item
#'
#' This is used for items that allow respondents to select multiple options from
#' a list, such as the symptoms items. Checking whether a specific selection is
#' selected in either "" (empty string) or `NA` responses will produce `NA`s, so
#' that empty responses are treated as missing, rather than as the item not
#' being selected.
#'
#' @param vec A list whose entries are character vectors, such as c("14", "15"),
#'   as produced by `split_options()`.
#' @param selection one string, such as "14", representing the answer choice of
#'   interest
#' @return a logical vector; for each entry in `vec`, the boolean indicates
#'   whether `selection` is contained in the character vector.
#' @examples
#' \dontrun{
#' symptoms <- split_options(data$B2)
#'
#' # vector of T/F/NA for each respondent's fever status
#' fever <- is_selected(symptoms, "1")
#' }
is_selected <- function(vec, selection) {
  selections <- unlist(lapply(
    vec,
    function(resp) {
      if (length(resp) == 0 || all(is.na(resp))) {
        # Qualtrics files code no selection as "" (empty string), which is
        # parsed by `read_csv()` as `NA` (missing) by default. Since all our
        # selection items include "None of the above" or similar, treat both no
        # selection ("") or missing (NA) as missing, for generality.
        NA
      } else {
        selection %in% resp
      }
    }))

  return(selections)
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
