-- This file contains a schema definition for MySQL storage
-- used by Mycroft Holmes
CREATE TABLE `features_metrics` (
  `entry_id` int(9) NOT NULL AUTO_INCREMENT,
  `feature` varchar(32) NOT NULL,
  `metric` varchar(32) NOT NULL,
  `value` int(9) NOT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`entry_id`),
  KEY `feature_metric_timestamp_idx` (`feature`,`metric`,`timestamp`)
) CHARSET=utf8;

-- https://dev.mysql.com/doc/refman/8.0/en/fixed-point-types.html
-- 20 is the precision and 2 is the scale
ALTER TABLE `features_metrics` CHANGE `value` `value` DECIMAL(20, 2) NOT NULL;
