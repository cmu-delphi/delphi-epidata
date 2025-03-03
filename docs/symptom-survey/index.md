---
title: <i>inactive</i> COVID-19 Trends and Impact Survey
nav_order: 4
---

# COVID-19 Trends and Impact Survey (CTIS)

From April 2020 to June 2022, Delphi conducted a voluntary survey about
COVID-19, distributed daily to users in the United States via a partnership with
Facebook. This survey asked respondents about COVID-like symptoms, their
behavior (such as social distancing), mental health, and economic and health
impacts they have experienced as a result of the pandemic. A high-level overview
of the survey is posted [on the Delphi
website](https://delphi.cmu.edu/epidemic-signals/ctis/), and an international
version is [conducted by the University of Maryland](https://covidmap.umd.edu/).
Data collection [ceased on June 25, 2022](end-of-survey.md).

This survey was also known unofficially as the Facebook Survey.

More survey details are also available [on the COVID-19 Trends and Impact Survey 2020-2022 (inactive) page](https://cmu-delphi.github.io/delphi-epidata/api/covidcast-signals/fb-survey.html) under the COVIDcast Main Endpoint's Data Source and Signals section of this API documentation site. 

The survey dataset is now archived via ICPSR:

* Reinhart, Alex, Mejia, Robin, and Tibshirani, Ryan J. COVID-19 Trends and
  Impact Survey (CTIS), United States, 2020-2022. Inter-university Consortium
  for Political and Social Research [distributor], 2025-02-28.
  <https://doi.org/10.3886/ICPSR39207.v1>

The archive includes complete documentation, including a Methodology Report on
survey design, a survey weighting guide, guides to the aggregate and microdata,
and example code. Aggregate contingency tables are available for public download
and restricted microdata can be obtained upon request. If you are a researcher
and would like to get access to the data, see our page on getting [data
access](data-access.md).

If you have questions about the survey or getting access to data, contact us at
<delphi-survey-info@lists.andrew.cmu.edu>.

## Results

The [survey results dashboard](https://delphi.cmu.edu/covidcast/survey-results/)
provides a high-level summary of survey results. Geographically aggregated data
from this survey is publicly available through the [COVIDcast API](../api/covidcast.md)
as the [`fb-survey` data source](../api/covidcast-signals/fb-survey.md). Demographic breakdowns of survey
data are publicly available as [downloadable contingency tables](contingency-tables.md).

CTIS data has been used in [numerous peer-reviewed publications](publications.md).

## Credits

The US COVID-19 Trends and Impact Survey (CTIS) is a project of the [Delphi
Group](https://delphi.cmu.edu/) at Carnegie Mellon University. Team members
include:

* [Alex Reinhart](https://www.refsmmat.com/), Principal Investigator
* Wichada La Motte-Kerr, Survey Coordinator (2020-2022)
* Robin Mejia, survey advisor
* Nat DeFries, statistical developer and data engineer
* Eu Jing Chua (2020-2021) and Mashrin Srivastava (2021-2022), data analysis
  interns
* plus support from many members of the [Delphi
  team](https://delphi.cmu.edu/about/team/)

The survey protocol is reviewed by the Carnegie Mellon University Institutional
Review Board.

The support of several institutions makes the survey possible. Facebook
supported the survey through recruitment (participants are invited via their
News Feed), survey sampling and weighting procedures, technical assistance in
survey design and implementation, and coordination with researchers and public
health officials. The University of Maryland's Social Data Science Center
conducted a [global version of the survey](https://covidmap.umd.edu/), and we
coordinated closely on survey design and implementation. Delphi collected,
aggregated, and distributes the US survey data, and retains ultimate
responsibility for the US survey instrument and data.

## Citing the Survey

Researchers who use the US survey data for research are asked to credit and cite
the survey in publications based on the data. Specifically, we ask that you:

1. Include the acknowledgment "This research is based on survey results from
   Carnegie Mellon University’s Delphi Group."
2. Cite our paper describing the survey:

    > Joshua A. Salomon, Alex Reinhart, Alyssa Bilinski, Eu Jing Chua, Wichada
    > La Motte-Kerr, Minttu M. Rönn, Marissa Reitsma, Katherine Ann Morris,
    > Sarah LaRocca, Tamar Farag, Frauke Kreuter, Roni Rosenfeld, and Ryan J.
    > Tibshirani (2021). "The US COVID-19 Trends and Impact Survey: Continuous
    > real-time measurement of COVID-19 symptoms, risks, protective behaviors,
    > testing, and vaccination", *Proceedings of the National Academy of
    > Sciences* 118 (51) e2111454118. <https://doi.org/10.1073/pnas.2111454118>

3. The data use agreement requires that if you disclose survey microdata, Delphi
   must agree on the aggregation method that you will use to ensure reported
   estimates do not disclose any individual identifiable information, including
   individual survey results. If you are unsure whether a particular aggregation
   will prevent disclosure of individual survey results, please email us at
   <delphi-survey-info@lists.andrew.cmu.edu>.
4. Finally, please notify us when your research is published. If you obtained
   the data via ICPSR, please [visit their
   site](https://www.icpsr.umich.edu/web/ICPSR/studies/39207) to find the form
   to submit data-related publications; otherwise, send a copy of your
   publication to <delphi-survey-info@lists.andrew.cmu.edu>.

When referring to the survey in text, we prefer the following formats:

* Long form (such as in an introduction or methods description): "The Delphi
  Group at Carnegie Mellon University U.S. COVID-19 Trends and Impact Survey, in
  partnership with Facebook".
* Short form (used after the long form has been introduced): "The U.S. COVID-19
  Trends and Impact Survey"
* Acronym form: "Delphi US CTIS"

Prior to July 2021, the survey was known as the COVID Symptom Survey (CSS), and
some older documentation and publications may still refer to this name. We
prefer that new publications and materials refer to the new name.
