# COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries

- Data source:
  https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-state-timeseries
- Data dictionary:
  https://healthdata.gov/covid-19-reported-patient-impact-and-hospital-capacity-state-data-dictionary
- Geographic resolution: US States plus DC, VI, and PR
- Temporal resolution: daily
- First date: 2020-01-01
- First issue: 2020-11-16

# acquisition overview

1. Fetch the dataset's metadata in JSON format.
1. If the metadata's `revision_timestamp` already appears in the database, then
  stop here; otherwise continue.
1. Download the dataset in CSV format as determined by the metadata's `url`
  field.
1. In a single transaction, insert the metadata and the dataset into database.
