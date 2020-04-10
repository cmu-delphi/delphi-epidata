# COVID-19 Survey

- COVID-19 survey is headed by CMU, implemented on qualtrics platform, and
  available exclusively through facebook platform
- any other source claiming to offer this survey should not be trusted
  - however this is subject to change
  - this page to remain the source of truth
- contribution is a novel data stream to assist with pandemic response efforts
- our sincere thanks if you have contributed by responding to the survey

# motivation

- problem is lack of situational awareness in ongoing pandemic
- want a high-resolution (county), high-coverage (national), low-latency (<24
  hour) signal of covid incidence
- solution is to collect anonymously reported health status from volunteers
  around the country, like you

# about the survey

- designed by cmu with input from others
- IRB approved
- launched 2020-04-06
- implemented via qualtrics for privacy
- entirely voluntary
- collects no personal data other than what is self-reported
- individual responses only visible to subset of delphi research group at CMU,
  and to select academic research partners
- questions were chosen to help identify/differentiate illness
- allows to estimate pandemic burden in real-time
- important signal for public health guidance and intervention
- useful signal for research involving outbreak detection and pandemic
  forecasting

# derived signals

- two derived signals:
  - influenza-like illness (ILI)
  - covid-19-like illness (CLI)
- individual-level ILI/CLI are binary classification from subset of questions
- individual-level ILI/CLI are each aggregated over either:
  - time (weekly)
    per county
  - space (hospital referral region, see https://www.dartmouthatlas.org/faq/)
    per day
- require 100 responses per aggregation, otherwise drop, for privacy

# data access

- aggregate ILI/CLI, plus standard deviation and sample size, openly available
  through Delphi Epidata API
- samples at a glance
  - url for some HHR on some day
  - python snippet of the same
- link to `covid_survey_*` endpoint documentation (to be written)
- link to client libraries
- links to data license and citation info

# contact

- point of contact
