ALTER TABLE flusurv ADD (
    `season` char(7) DEFAULT NULL,

    `rate_age_18t29` double DEFAULT NULL,
    `rate_age_30t39` double DEFAULT NULL,
    `rate_age_40t49` double DEFAULT NULL,
    `rate_age_5t11` double DEFAULT NULL,
    `rate_age_12t17` double DEFAULT NULL,
    `rate_age_lt18` double DEFAULT NULL,
    `rate_age_gte18` double DEFAULT NULL,
    `rate_age_1t4` double DEFAULT NULL,
    `rate_age_gte75` double DEFAULT NULL,
    `rate_age_0tlt1` double DEFAULT NULL,
    `rate_race_white` double DEFAULT NULL,
    `rate_race_black` double DEFAULT NULL,
    `rate_race_hisp` double DEFAULT NULL,
    `rate_race_asian` double DEFAULT NULL,
    `rate_race_natamer` double DEFAULT NULL,
    `rate_sex_male` double DEFAULT NULL,
    `rate_sex_female` double DEFAULT NULL,
    `rate_flu_a` double DEFAULT NULL,
    `rate_flu_b` double DEFAULT NULL
);
