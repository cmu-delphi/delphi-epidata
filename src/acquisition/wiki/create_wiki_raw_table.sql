CREATE TABLE `wiki_raw` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `hash` char(32) NOT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `size` int(11) DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  `worker` varchar(256) DEFAULT NULL,
  `elapsed` float DEFAULT NULL,
  `data` varchar(2048) DEFAULT NULL,
  UNIQUE KEY `name` (`name`),
  KEY `status` (`status`)
);

# Alter the column type because we need larger space as we extract more articles
ALTER TABLE `wiki_raw` MODIFY COLUMN `data` varchar(4096);

