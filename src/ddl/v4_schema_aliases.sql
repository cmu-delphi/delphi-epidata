-- ----------------------------------
-- NOTE: this file ("v4_schema_aliases.sql") is deliberately named to be ordering-sensitive:
--       it must be executed *AFTER* "v4_schema.sql" to ensure referenced tables exist.
-- NOTE: v4-related db schema name change from `epidata` to `covid` is only implemented in acquisition code.
--       frontend api code still uses `epidata` but has these relevant tables/views "aliased" to use covid.blah when referred to as epidata.blah in context.
-- ----------------------------------

CREATE VIEW `epidata`.`epimetric_full_v`     AS SELECT * FROM `covid`.`epimetric_full_v`;
CREATE VIEW `epidata`.`epimetric_latest_v`   AS SELECT * FROM `covid`.`epimetric_latest_v`;
CREATE VIEW `epidata`.`covidcast_meta_cache` AS SELECT * FROM `covid`.`covidcast_meta_cache`;
