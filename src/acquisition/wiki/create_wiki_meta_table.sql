CREATE TABLE `wiki_meta`(
  `id`            INT(11)      NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `datetime`      DATETIME     NOT NULL                           ,
  `date`          date         NOT NULL                           ,
  `epiweek`       INT(11)      NOT NULL                           ,
  `total`         INT(11)      NOT NULL                           ,
  UNIQUE KEY `datetime` (`datetime`)
);

# Add a column `language` to the wiki_meta table
ALTER TABLE `wiki_meta`
ADD `language` CHAR(2) NOT NULL DEFAULT 'en';

# Another step is to update the UNIQUE KEY
ALTER TABLE `wiki_meta`
  DROP INDEX `datetime`,
  ADD UNIQUE KEY `datetime` (`datetime`, `language`);

