CREATE TABLE `wiki`(
  `id`            INT(11)      NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `datetime`      DATETIME     NOT NULL                           ,
  `article`       VARCHAR(64)  NOT NULL                           ,
  `count`         INT(11)      NOT NULL                           ,
  UNIQUE KEY `datetime` (`datetime`, `article`),
  KEY `datetime_2` (`datetime`),
  KEY `article` (`article`)
);

# Add a column `language` to the wiki table
ALTER TABLE `wiki`
ADD `language` CHAR(2) NOT NULL DEFAULT 'en';

# Another step is to update the UNIQUE KEY
ALTER TABLE `wiki`
  DROP INDEX `datetime`,
  ADD UNIQUE KEY `datetime` (`datetime`, `article`, `language`);
