-- This file contains a schema definition for MySQL storage
-- used by Mycroft Holmes
CREATE TABLE `features_metrics` (
  `entry_id` int(9) NOT NULL AUTO_INCREMENT,
  `feature` varchar(32) NOT NULL,
  `metric` varchar(32) NOT NULL,
  `value` int(9) NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`entry_id`),
  KEY `feature_metric_timestamp_idx` (`feature`,`metric`,`timestamp`)
) CHARSET=utf8;
