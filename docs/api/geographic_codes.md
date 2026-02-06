---
title: Geographic Codes
parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 900
---

# Geographic Codes
{: .no_toc}

This page documents the valid geographic codes accepted by various API endpoints.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Countries and Territories in the Americas

Multiple endpoints accept ISO 3166-1 alpha-2 country codes for countries and territories in the Americas.

{: .note}
> **Note:** While the API accepts codes for all countries listed below, data may not be available for every country or territory.

### Supported Codes

| Code | Name |
|---|---|
| `AG` | Antigua and Barbuda |
| `AI` | Anguilla |
| `AR` | Argentina |
| `AW` | Aruba |
| `BB` | Barbados |
| `BL` | Saint Barthelemy |
| `BM` | Bermuda |
| `BO` | Bolivia |
| `BQ` | Bonaire, Saint Eustatius and Saba |
| `BR` | Brazil |
| `BS` | Bahamas |
| `BZ` | Belize |
| `CA` | Canada |
| `CL` | Chile |
| `CO` | Colombia |
| `CR` | Costa Rica |
| `CU` | Cuba |
| `CW` | Curaçao |
| `DO` | Dominican Republic |
| `EC` | Ecuador |
| `GD` | Grenada |
| `GF` | French Guiana |
| `GP` | Guadeloupe |
| `GT` | Guatemala |
| `GY` | Guyana |
| `HN` | Honduras |
| `HT` | Haiti |
| `JM` | Jamaica |
| `KN` | Saint Kitts and Nevis |
| `KY` | Cayman Islands |
| `LC` | Saint Lucia |
| `MF` | Saint Martin (French part) |
| `MQ` | Martinique |
| `MS` | Montserrat |
| `MX` | Mexico |
| `NI` | Nicaragua |
| `PA` | Panama |
| `PE` | Peru |
| `PR` | Puerto Rico |
| `PY` | Paraguay |
| `SR` | Suriname |
| `SV` | El Salvador |
| `SX` | Sint Maarten (Dutch part) |
| `TC` | Turks and Caicos Islands |
| `TT` | Trinidad and Tobago |
| `US` | United States of America |
| `UY` | Uruguay |
| `VC` | Saint Vincent and the Grenadines |
| `VE` | Venezuela |
| `VG` | Virgin Islands (UK) |
| `VI` | Virgin Islands (US) |

<!--- Countries with no responses
| FK | Falkland Islands |
| GL | Greenland |
| GS | South Georgia and the South Sandwich Islands |
| PM | Saint Pierre and Miquelon --->

## US Regions and States

Multiple endpoints use standard US geographic codes. These include the national code, HHS regions, Census divisions, and state codes.

### National Code

| Code | Name |
|---|---|
| `nat` | United States (National) |

### HHS Regions

The US Department of Health and Human Services divides the country into 10 regions.

| Code | Region | States |
|---|---|---|
| `hhs1` | Region 1 | CT, ME, MA, NH, RI, VT |
| `hhs2` | Region 2 | NJ, NY, PR, VI |
| `hhs3` | Region 3 | DE, DC, MD, PA, VA, WV |
| `hhs4` | Region 4 | AL, FL, GA, KY, MS, NC, SC, TN |
| `hhs5` | Region 5 | IL, IN, MI, MN, OH, WI |
| `hhs6` | Region 6 | AR, LA, NM, OK, TX |
| `hhs7` | Region 7 | IA, KS, MO, NE |
| `hhs8` | Region 8 | CO, MT, ND, SD, UT, WY |
| `hhs9` | Region 9 | AZ, CA, HI, NV, AS, GU, MP |
| `hhs10` | Region 10 | AK, ID, OR, WA |

### Census Divisions

The US Census Bureau divides the country into 9 divisions.

| Code | Division | States |
|---|---|---|
| `cen1` | New England | CT, ME, MA, NH, RI, VT |
| `cen2` | Mid-Atlantic | NJ, NY, PA |
| `cen3` | East North Central | IL, IN, MI, OH, WI |
| `cen4` | West North Central | IA, KS, MN, MO, NE, ND, SD |
| `cen5` | South Atlantic | DE, DC, FL, GA, MD, NC, SC, VA, WV |
| `cen6` | East South Central | AL, KY, MS, TN |
| `cen7` | West South Central | AR, LA, OK, TX |
| `cen8` | Mountain | AZ, CO, ID, MT, NV, NM, UT, WY |
| `cen9` | Pacific | AK, CA, HI, OR, WA |

### US States and Territories

Full list of 51 US states and territories used by multiple endpoints:

#### US States

| Code | Name |
|---|---|
| `AK` | Alaska |
| `AL` | Alabama |
| `AR` | Arkansas |
| `AZ` | Arizona |
| `CA` | California |
| `CO` | Colorado |
| `CT` | Connecticut |
| `DC` | District of Columbia |
| `DE` | Delaware |
| `FL` | Florida |
| `GA` | Georgia |
| `HI` | Hawaii |
| `IA` | Iowa |
| `ID` | Idaho |
| `IL` | Illinois |
| `IN` | Indiana |
| `KS` | Kansas |
| `KY` | Kentucky |
| `LA` | Louisiana |
| `MA` | Massachusetts |
| `MD` | Maryland |
| `ME` | Maine |
| `MI` | Michigan |
| `MN` | Minnesota |
| `MO` | Missouri |
| `MS` | Mississippi |
| `MT` | Montana |
| `NC` | North Carolina |
| `ND` | North Dakota |
| `NE` | Nebraska |
| `NH` | New Hampshire |
| `NJ` | New Jersey |
| `NM` | New Mexico |
| `NV` | Nevada |
| `NY` | New York |
| `OH` | Ohio |
| `OK` | Oklahoma |
| `OR` | Oregon |
| `PA` | Pennsylvania |
| `RI` | Rhode Island |
| `SC` | South Carolina |
| `SD` | South Dakota |
| `TN` | Tennessee |
| `TX` | Texas |
| `UT` | Utah |
| `VA` | Virginia |
| `VT` | Vermont |
| `WA` | Washington |
| `WI` | Wisconsin |
| `WV` | West Virginia |
| `WY` | Wyoming |

#### US Territories

| Code | Name |
|---|---|
| `PR` | Puerto Rico |
| `VI` | Virgin Islands |
| `GU` | Guam |
| `AS` | American Samoa |
| `MP` | Northern Mariana Islands |
| `FM` | Federated States of Micronesia |
| `MH` | Marshall Islands |
| `PW` | Palau |

## Selected US cities

Selected US cities used by multiple endpoints.

| Code | Name |
|---|---|
| `Abilene_TX` | Abilene, TX |
| `Akron_OH` | Akron, OH |
| `Albany_NY` | Albany, NY |
| `Albuquerque_NM` | Albuquerque, NM |
| `Alexandria_VA` | Alexandria, VA |
| `Allentown_PA` | Allentown, PA |
| `Amarillo_TX` | Amarillo, TX |
| `Anaheim_CA` | Anaheim, CA |
| `Anchorage_AK` | Anchorage, AK |
| `Ann_Arbor_MI` | Ann Arbor, MI |
| `Arlington_TX` | Arlington, TX |
| `Arlington_VA` | Arlington, VA |
| `Atlanta_GA` | Atlanta, GA |
| `Austin_TX` | Austin, TX |
| `Bakersfield_CA` | Bakersfield, CA |
| `Baltimore_MD` | Baltimore, MD |
| `Baton_Rouge_LA` | Baton Rouge, LA |
| `Berkeley_CA` | Berkeley, CA |
| `Birmingham_AL` | Birmingham, AL |
| `Boise_ID` | Boise, ID |
| `Boston_MA` | Boston, MA |
| `Boulder_CO` | Boulder, CO |
| `Buffalo_NY` | Buffalo, NY |
| `Cary_NC` | Cary, NC |
| `Charlotte_NC` | Charlotte, NC |
| `Chicago_IL` | Chicago, IL |
| `Cleveland_OH` | Cleveland, OH |
| `Colorado_Springs_CO` | Colorado Springs, CO |
| `Columbia_SC` | Columbia, SC |
| `Columbus_OH` | Columbus, OH |
| `Dallas_TX` | Dallas, TX |
| `Dayton_OH` | Dayton, OH |
| `Denver_CO` | Denver, CO |
| `Des_Moines_IA` | Des Moines, IA |
| `Durham_NC` | Durham, NC |
| `Eugene_OR` | Eugene, OR |
| `Fresno_CA` | Fresno, CA |
| `Ft_Worth_TX` | Ft Worth, TX |
| `Gainesville_FL` | Gainesville, FL |
| `Grand_Rapids_MI` | Grand Rapids, MI |
| `Greensboro_NC` | Greensboro, NC |
| `Greenville_SC` | Greenville, SC |
| `Honolulu_HI` | Honolulu, HI |
| `Houston_TX` | Houston, TX |
| `Indianapolis_IN` | Indianapolis, IN |
| `Irvine_CA` | Irvine, CA |
| `Irving_TX` | Irving, TX |
| `Jacksonville_FL` | Jacksonville, FL |
| `Jackson_MS` | Jackson, MS |
| `Kansas_City_MO` | Kansas City, MO |
| `Knoxville_TN` | Knoxville, TN |
| `Las_Vegas_NV` | Las Vegas, NV |
| `Lexington_KY` | Lexington, KY |
| `Lincoln_NE` | Lincoln, NE |
| `Little_Rock_AR` | Little Rock, AR |
| `Los_Angeles_CA` | Los Angeles, CA |
| `Lubbock_TX` | Lubbock, TX |
| `Madison_WI` | Madison, WI |
| `Memphis_TN` | Memphis, TN |
| `Mesa_AZ` | Mesa, AZ |
| `Miami_FL` | Miami, FL |
| `Milwaukee_WI` | Milwaukee, WI |
| `Nashville_TN` | Nashville, TN |
| `Newark_NJ` | Newark, NJ |
| `New_Orleans_LA` | New Orleans, LA |
| `New_York_NY` | New York, NY |
| `Norfolk_VA` | Norfolk, VA |
| `Oakland_CA` | Oakland, CA |
| `Oklahoma_City_OK` | Oklahoma City, OK |
| `Omaha_NE` | Omaha, NE |
| `Orlando_FL` | Orlando, FL |
| `Philadelphia_PA` | Philadelphia, PA |
| `Phoenix_AZ` | Phoenix, AZ |
| `Pittsburgh_PA` | Pittsburgh, PA |
| `Plano_TX` | Plano, TX |
| `Portland_OR` | Portland, OR |
| `Providence_RI` | Providence, RI |
| `Raleigh_NC` | Raleigh, NC |
| `Reno_NV` | Reno, NV |
| `Reston_VA` | Reston, VA |
| `Richmond_VA` | Richmond, VA |
| `Rochester_NY` | Rochester, NY |
| `Roswell_GA` | Roswell, GA |
| `Sacramento_CA` | Sacramento, CA |
| `Salt_Lake_City_UT` | Salt Lake City, UT |
| `Santa_Clara_CA` | Santa Clara, CA |
| `San_Antonio_TX` | San Antonio, TX |
| `San_Diego_CA` | San Diego, CA |
| `San_Francisco_CA` | San Francisco, CA |
| `San_Jose_CA` | San Jose, CA |
| `Scottsdale_AZ` | Scottsdale, AZ |
| `Seattle_WA` | Seattle, WA |
| `Somerville_MA` | Somerville, MA |
| `Spokane_WA` | Spokane, WA |
| `Springfield_MO` | Springfield, MO |
| `State_College_PA` | State College, PA |
| `St_Louis_MO` | St Louis, MO |
| `St_Paul_MN` | St Paul, MN |
| `Sunnyvale_CA` | Sunnyvale, CA |
| `Tampa_FL` | Tampa, FL |
| `Tempe_AZ` | Tempe, AZ |
| `Tucson_AZ` | Tucson, AZ |
| `Tulsa_OK` | Tulsa, OK |
| `Washington_DC` | Washington, DC |
| `Wichita_KS` | Wichita, KS |

## NIDSS

Geographic codes used by [NIDSS Flu](nidss_flu.html) and [NIDSS Dengue](nidss_dengue.html) endpoints.

### Taiwan Regions

Regions of Taiwan.

| Code | Name |
|---|---|
| `nationwide` | Nationwide |
| `central` | Central |
| `eastern` | Eastern |
| `kaoping` | Kaoping |
| `northern` | Northern |
| `southern` | Southern |
| `taipei` | Taipei |

### Taiwan Cities and Counties

Administrative divisions of Taiwan.

| Code | Name |
|---|---|
| `changhua_county` | Changhua County |
| `chiayi_city` | Chiayi City |
| `chiayi_county` | Chiayi County |
| `hsinchu_city` | Hsinchu City |
| `hsinchu_county` | Hsinchu County |
| `hualien_county` | Hualien County |
| `kaohsiung_city` | Kaohsiung City |
| `keelung_city` | Keelung City |
| `kinmen_county` | Kinmen County |
| `lienchiang_county` | Lienchiang County |
| `miaoli_county` | Miaoli County |
| `nantou_county` | Nantou County |
| `new_taipei_city` | New Taipei City |
| `penghu_county` | Penghu County |
| `pingtung_county` | Pingtung County |
| `taichung_city` | Taichung City |
| `tainan_city` | Tainan City |
| `taipei_city` | Taipei City |
| `taitung_county` | Taitung County |
| `taoyuan_city` | Taoyuan City |
| `yilan_county` | Yilan County |
| `yunlin_county` | Yunlin County |

## European Countries

European countries and regions used by the [ECDC ILI](ecdc_ili.html) endpoint.

| Code | Name |
|---|---|
| `armenia` | Armenia |
| `austria` | Austria |
| `azerbaijan` | Azerbaijan |
| `belarus` | Belarus |
| `belgium` | Belgium |
| `czech republic` | Czech Republic |
| `denmark` | Denmark |
| `estonia` | Estonia |
| `finland` | Finland |
| `france` | France |
| `georgia` | Georgia |
| `iceland` | Iceland |
| `ireland` | Ireland |
| `israel` | Israel |
| `italy` | Italy |
| `kazakhstan` | Kazakhstan |
| `kosovo*` | Kosovo* |
| `kyrgyzstan` | Kyrgyzstan |
| `latvia` | Latvia |
| `lithuania` | Lithuania |
| `luxembourg` | Luxembourg |
| `malta` | Malta |
| `moldova` | Moldova |
| `montenegro` | Montenegro |
| `netherlands` | Netherlands |
| `north macedonia` | North Macedonia |
| `norway` | Norway |
| `poland` | Poland |
| `portugal` | Portugal |
| `romania` | Romania |
| `russia` | Russia |
| `serbia` | Serbia |
| `slovakia` | Slovakia |
| `slovenia` | Slovenia |
| `spain` | Spain |
| `switzerland` | Switzerland |
| `tajikistan` | Tajikistan |
| `turkey` | Turkey |
| `turkmenistan` | Turkmenistan |
| `ukraine` | Ukraine |
| `united kingdom - england` | United Kingdom - England |
| `united kingdom - northern irel` | United Kingdom - Northern Irel |
| `united kingdom - scotland` | United Kingdom - Scotland |
| `united kingdom - wales` | United Kingdom - Wales |
| `uzbekistan` | Uzbekistan |

## FluSurv Locations

Locations used by the [FluSurv](flusurv.html) endpoint.

| Code | Description |
|---|---|
| `CA` | California |
| `CO` | Colorado |
| `CT` | Connecticut |
| `GA` | Georgia |
| `IA` | Iowa |
| `ID` | Idaho |
| `MD` | Maryland |
| `MI` | Michigan |
| `MN` | Minnesota |
| `NM` | New Mexico |
| `NY_albany` | New York (Albany) |
| `NY_rochester` | New York (Rochester) |
| `OH` | Ohio |
| `OK` | Oklahoma |
| `OR` | Oregon |
| `RI` | Rhode Island |
| `SD` | South Dakota |
| `TN` | Tennessee |
| `UT` | Utah |
| `network_all` | All Networks |
| `network_eip` | Emerging Infections Program |
| `network_ihsp` | Influenza Hospitalization Surveillance Project |

## Republic of Korea

Geographic codes used by the [KCDC ILI](kcdc_ili.html) endpoint.

| Code | Name |
|---|---|
| `ROK` | Republic of Korea |


## FluView Cities

Specific cities used by the [FluView](fluview.html) endpoint.

| City | Code |
|---|---|
| Chicago | `ord` |
| Los Angeles | `lax` |
| New York City | `jfk` |

### Note on New York

In the CDC FluView system, New York State and New York City are often reported separately.
* `ny_minus_jfk` represents New York State **excluding** NYC.
* `jfk` represents New York City.
* `ny` represents the entire state (the sum of the two).
