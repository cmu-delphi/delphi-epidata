# HHS COVID-19 Patient Impact and Hospital Capacity

HHS has four (as of writing) datasets relating to patient impact and hospital
capacity, collectively referred to as "covid_hosp" here. In short, they are:

- [COVID-19 **Reported** Patient Impact and Hospital Capacity by **State Timeseries**](https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-state-timeseries)

    A _daily_ timeseries of ~60 fields for US states, updated ~weekly. This is
    a weekly roll-up of "COVID-19 **Reported** Patient Impact and Hospital
    Capacity by **State**", over all weeks.

    See [acquisition details](state_timeseries/README.md).

- [COVID-19 **Reported** Patient Impact and Hospital Capacity by **State**](https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-state)

    A _daily_ snapshot of ~60 fields for US states, updated ~daily. This is a
    daily snapshot of "COVID-19 **Reported** Patient Impact and Hospital
    Capacity by **State Timeseries**", for the most recently available date.
    Because it's per day, rather than week, it's the most up-to-date source of
    _reported, state-level_ data. However, since the data is preliminary, it is
    subject to greater missingness and larger revisions.

    See [acquisition details](state_daily/README.md).

- [COVID-19 **Estimated** Patient Impact and Hospital Capacity by **State**](https://healthdata.gov/dataset/covid-19-estimated-patient-impact-and-hospital-capacity-state)

    An early _estimate_ of "COVID-19 **Reported** Patient Impact and Hospital
    Capacity by **State**". This dataset currently seems to lack a data
    dictionary.

    We do not yet acquire this data source.

- [COVID-19 **Reported** Patient Impact and Hospital Capacity by **Facility**](https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-facility)

    A _weekly_ timeseries of ~90 fields for individual healthcare facilities,
    updated ~weekly. Compared to "COVID-19 **Reported** Patient Impact and
    Hospital Capacity by **State Timeseries**", this dataset has lower temporal
    resolution (weekly vs daily) but greatly increased geographic resolution
    (street address vs state).

    See [acquisition details](facility/README.md).


# common acquisition overview

1. Fetch the dataset's metadata in JSON format.
1. If the metadata's `revision_timestamp` already appears in the database, then
  stop here; otherwise continue.
1. Download the dataset in CSV format as determined by the metadata's `url`
  field.
1. In a single transaction, insert the metadata and the dataset into database.
