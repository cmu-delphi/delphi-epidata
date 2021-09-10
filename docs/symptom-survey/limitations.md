---
title: Survey Limitations
parent: COVID-19 Trends and Impact Survey
nav_order: 9
---

# Survey Limitations
{: .no_toc}

The COVID-19 Trends and Impact Survey (CTIS) gathers large amounts of detailed
data; however, it is not perfect, and its design means it is subject to several
crucial limitations. Anyone using the data to make policy decisions or answer
research questions should be aware of these limitations. Given these
limitations, we recommend using the data to:

- Track changes over time, such as to monitor sudden increases in reported
  symptoms or changes in reported vaccination attitudes.
- Make comparisons across space, such as to identify regions with much higher or
  lower values.
- Make comparisons between groups, such as between occupational or age groups,
  keeping in mind any [sample limitations](#the-sample) that might affect these
  comparisons.
- Augment data collected from other sources, such as more rigorously controlled
  surveys with high response rates.

We do **not** recommend using CTIS data to

- Make point estimates of population quantities (such as the exact percentage of
  people who meet a certain criterion) without reference to other data sources.
  Because of sampling, weighting, and response biases, such estimates can be
  biased, and standard confidence intervals and hypothesis tests will be
  misleading.
- Analyze very small or localized demographic subgroups. Due to the [response
  behavior issues](#response-behavior) discussed below, there is measurement
  error in the demographic data. Very small demographic groups may
  disproportionately include respondents who pick their demographics at random
  or attempt to disrupt the survey in other ways, even if those respondents are
  rare overall.

The sections below explain these limitations in more detail.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## The Sample

Facebook takes a random sample of active adult users every day and invites them
to complete the survey. ("Adult" means the user has indicated they are least 18
years old in their profile.) Taking the survey is voluntary, and only 1-2% of those
users who are invited actually take the survey. This leaves opportunities for
sampling bias, if the sample is construed to represent the US adult population:

1. **Sampling frame.** The sample is random and maintains similar user
   characteristics each day, but it is drawn from adult Facebook active users
   who use one of the languages the survey is translated into: English [American
   and British], Spanish [Spain and Latin American], French, Brazilian
   Portuguese, Vietnamese, and simplified Chinese. This is not the United States
   population as a whole. While [most American adults use
   Facebook](https://www.pewresearch.org/internet/2021/04/07/social-media-use-in-2021/)
   and the available languages are more comprehensive than for many public
   health surveys, "most" is not the same as "all", and some demographic groups
   may be poorly represented in the Facebook sample.
2. **Non-response bias.** Only a small fraction of invited users choose to take
   the survey when they are invited. If their decision on whether to take the
   survey is random, this is not a problem. However, their decision to take the
   survey may be correlated with other factors---such as their level of concern
   about COVID-19 or their trust of academic researchers. If that is the case,
   the sample will disproportionately contain people with certain attitudes and
   beliefs.

Facebook calculates [survey weights](weights.md) ([see below](#weighting)) that
are intended to help correct for these issues. The weights adjust the age and
gender distribution of the respondents to match Census data, and adjust for
non-response by using a model for the probability of any user to click on the
survey link. However, if that non-response model is not perfect (for example,
non-response varies with respondent attributes not included in the model), or if
the Facebook population differs from the US population on more features than
just age and gender, the weights will not account for all sampling biases. For
example, analyses of weighted survey data shows demographics relatively similar
to the US population, with slightly higher levels of education and a smaller
proportion of non-white respondents; however, comparisons of self-reported
vaccination rates of survey respondents with CDC US population benchmarks
indicate that CTIS respondents are more likely to be vaccinated than the general
population.

We do, however, expect that any sampling biases will remain relatively
consistent over time, allowing us to make reliable comparisons over time (such
as noting an increase or decrease in vaccination rates or vaccine intent) even
if the point estimates are consistently biased. This is a common issue with
self-reported data; for example, surveys on illegal drug use expect
under-reporting (as they ask about an illegal activity) but are commonly used to
make comparisons between groups or over time.

Also, Facebook's sampling process allows users to be invited to the survey
repeatedly. A user will only be reinvited at least thirty days after their
previous invitation. Because respondents are anonymous and we do not receive any
unique identifiers, responses from the same user are not linked in any way.
Analysts must be aware that when working with responses submitted more than a
month apart, some responses may be from the same users.

## Weighting

It is important to **read the [weights documentation](weights.md)** to
understand how Facebook calculates survey weights and what they account for.
There are some key limitations:

1. Because we do not receive Facebook profile data and Facebook does not receive
   survey response data, the weights are based only on attributes in Facebook
   profiles, *not* on demographics reported in response to survey questions. For
   example, if a respondent's Facebook profile says they are 35 years old and
   live in Delaware, but on the survey they respond that they are 45 years old
   and live in Maryland, the weight will be calculated based on the profile
   information and reflect the Delaware location. This causes measurement error
   in the weights.
2. Similarly, the non-response model used by Facebook only uses information
   available to Facebook, such as profile information. As discussed above, if
   this model is not perfect, for example if factors not included in the model
  affect non-response, the weights will not fully account for this
   non-response bias.
3. Facebook only invites users who it believes reside in the 50 states or
   Washington, DC. (Puerto Rico is sampled separately as part of the
   [international version of the survey](https://covidmap.umd.edu/).) If
   Facebook believes a user qualifies, but the user then replies that they live
   in Puerto Rico or another US territory, their weight will be incorrect.
   Starting in September 2021, these responses are not included in any
   microdata.

## Response Behavior

Survey scientists have long known that humans do not always provide complete and
truthful responses to questions about their attributes, beliefs, and behaviors.
There are two primary reasons CTIS responses may be suspect.

First is **social desirability bias.** As with all self-report measurements,
survey respondents may give responses consistent with what they believe is
socially desirable, because they feel pressured to fit social norms. For
example, if someone lives in an area where masks are widely used and seen as
essential, they may report that they wear their mask most or all of the time
when in public, even if they don't. While this effect is likely smaller on an
anonymous online survey than in an in-person interview, it could still be
present.

The second problem is deliberate trolling. While intentional mis-reporting is
always a possibility when users provide self-report data, it is a particular
concern for a large, online survey on a controversial topic offered through a
large social media platform. It appears that the vast majority of CTIS
respondents complete the survey in good faith; however, we occasionally receive
emails from survey respondents gloating that they have deliberately provided
false responses to the survey, usually because they believe the COVID-19
pandemic is a conspiracy or that scientists are suppressing key information.

We have also observed problematic behavior in a specific subset of respondents.
While less than 1% of respondents opt to self-describe their own gender, a large
percentage of respondents who do choose that option provide a description that
is actually a protest against the question or the survey; for example, making
trans-phobic comments or [reporting their gender identification as “Attack
Helicopter”](https://knowyourmeme.com/memes/i-sexually-identify-as-an-attack-helicopter).
Additionally, these respondents disproportionately select specific demographic
groups, such as having a PhD, being over age 75, and being Hispanic, all at
rates far exceeding their overall presence in the US population, suggesting that
people who want to disrupt the survey also pick on specific groups to troll.

(Note that if a respondent is invited once but completes the survey multiple
times, or shares their unique link with friends to take it, only the first
response is counted; this limits the impact of deliberate trolling. If the
respondent is sampled and invited again later, they receive a new unique link.)

For overall estimates, trolling is not expected to impact results in a
meaningful way. However, given the concentration of trolls in small demographic
groups, users interested in comparisons of small demographic groups should
examine a sample of the raw data. For example, if you are interested in
responses from Hispanic adults over age 65, examine the other demographic
variables for this group of respondents to ensure they appear to match what you
would expect and do not appear influenced by respondents who give deliberately
strange answers.

Importantly, weights cannot correct for trolling behavior. Users can either note
any concerns they have when reporting for small groups, or they may choose to
analyze the data without a suspect group. We are continuing to evaluate trolling
and will provide updates if new patterns appear.

## Missing Data

Some survey respondents do not complete the entire survey. This could be because
they get impatient with it, because they do not want to respond to questions
about specific topics, or simply because they are responding to the survey
during a quick break or while waiting in line at Starbucks. (Remember, Facebook
users see the invitation when they're browsing the Facebook news feed, which
could be any time someone might pull out their phone and check Facebook.)

As a result, questions that appear later in the survey, including demographics,
can be blank in 10-20% of survey responses. Similar to overall non-response,
this is an issue when such behavior does not occur at random relative to the
questions you are analyzing; for example, if individuals who are particularly
concerned about COVID-19 are more likely to take the time to finish the survey.

Also, the CTIS survey instrument is deliberately designed so that most items are
optional---Qualtrics will not attempt to force respondents to answer questions
that they leave blank. This allows respondents to leave an item blank if they
prefer not to answer it, rather than entering a nonsense answer. This can lead
to missingness in the middle of the survey, even among respondents who answer
later questions. As noted above, this missingness is almost certainly not at
random. Data users should examine and report the missingness in the questions
they use. Imputation methods are an option; users should consider whether the
assumptions of imputation models appear to be met for the data.
