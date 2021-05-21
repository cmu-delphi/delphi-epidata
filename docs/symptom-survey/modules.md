---
title: Survey Modules & Randomization
parent: COVID Symptom Survey
nav_order: 7
---

# Questions and Coding
{: .no_toc}

To reduce the overall length of the instrument and minimize response burden, the
COVID Symptom Survey will consist of a block of daily core questions and will
use a randomized module approach for the other topics. Implementation of this
approach started in [Wave 11](coding.md#wave-11), which launched on May 20,
2021.

Each respondent invited to take the survey will be asked the daily core
questions. The daily core questions for Wave 11 include:

* Symptoms
* Testing
* COVID-19 vaccine
* Behaviors

After answering these questions, survey respondents will be randomly allocated
and evenly distributed to Module A or Module B.

Survey items in Module A cover the following topics:

* Beliefs and Norms
* Knowledge and Information
* Healthcare

Survey items in Module B cover the following topics:

* Well-being
* Parenting behaviors (including schooling)
* Specific demographic questions (i.e. cigarette use and pregnancy)

After the modules, the survey will conclude with asking respondents demographics
and occupation questions. It is also noteworthy that after randomization to
either Module A or B, the platform does not allow respondents to navigate back
to change their previous responses in the Daily Core questions.

Microdata files available to users with data use agreements include a `module`
column that indicates the module the respondent was randomly assigned to; this
column contains the values `A`, `B`, or `NA` (for respondents not assigned to a
module, e.g. because they completed a prior survey wave).
