ALTER TABLE covid_hosp_meta ADD COLUMN hhs_dataset_id CHAR(9) NOT NULL DEFAULT "????-????";
UPDATE covid_hosp_meta SET hhs_dataset_id="g62h-syeh" WHERE revision_timestamp LIKE "%g62h-syeh%";
UPDATE covid_hosp_meta SET hhs_dataset_id="6xf2-c3ie" WHERE revision_timestamp LIKE "%6xf2-c3ie%";
UPDATE covid_hosp_meta SET hhs_dataset_id="anag-cw7u" WHERE revision_timestamp LIKE "%anag-cw7u%";
