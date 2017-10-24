# FluView: ILINet data at the national, regional, and state/territorial level

## Overview

CDC publishes ILINet data for a number of regions via its [online FluView web app](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html). This data is updated weekly.

The scripts in this directory fetch that data and store it in a local database. This is especially important since the data is updated retrospectively in a process known informally as "backfill". Changes due to backfill are preserved, allowing us to better understand -- and even model -- how this data changes over time.

## The data

The most important value, for our purposes, is wILI -- weighted percent influenza-like illness. For a given location, this describes the percent of healthcare provider visits for which patients presented with flu-like symptoms. wILI is the population-weighted combination of (unweighted) ILI in the states that make up a given region. For states, wILI is trivially equal to ILI. Separate from wILI, ILI is also defined for regions, but we generally do no use it.

Nationally and regionally, we also have counts of the number of patients with ILI, broken down by age group.

## The process

First we fetch the metadata object from CDC. This contains, among many other things, the number of the most recent week for which data is currently available -- which we call the epiweek of "issue" -- and the list of available locations. This list includes the US as a whole ("national"), the 10 HHS regions, the 9 census divisions, and -- as of now -- 57 states and territories.

Given that metadata, we then fetch the most recent two seasons of ILINet data for each available location. This is done in batches for efficiency. Each tier -- national, regional, divisional, and territorial -- is downloaded separately.

Once the data files are downloaded, they are extracted, parsed, and filtered, and then the data is loaded into our local epidata database. If any past values are updated (i.e. due to backfill), then a new row is inserted. Otherwise, if the values are unchanged, then the existing row's metadata (e.g. fetch date) is updated.

Once in the database, the data is available through the [Delphi Epidata API](https://github.com/cmu-delphi/delphi-epidata).

## Terminology

The terms "fluview" and "ILINet" -- and to some extent, "wILI" -- are sometimes, and in some contexts, used interchangeably. Here's a more accurate description of each of those terms:

  - FluView is CDC's web app, which provides, among other things, ILINet data
    for several regions of the US.
  - ILINet is a nationwide outpatient surveillance program that collects data
    relating to influenza-like illness.
  - ILI is the percent of visits with influenza-like illness, out of total
    visits. wILI is a regional signal that is computed as the population-weighted average of state ILI. For simplicity, we further extend the idea of wILI to states and territories by trivially setting wILI in these locations equal to ILI.

In other words: (w)ILI is the data, ILINet is the network which produces the data, and FluView is the mechanism by which CDC makes the data publicly available.
