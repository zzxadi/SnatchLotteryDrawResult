CREATE TABLE `t_lottery_draw_src` (
  `Fsrc_no` varchar(32) NOT NULL,
  `Flottery_id` varchar(32) NOT NULL,
  `Fsrc_name` varchar(64) NOT NULL,
  `Fstate` int(11) NOT NULL DEFAULT '1',
  `Fpriority` int(11) NOT NULL DEFAULT '0',
  `Fcreate_time` datetime NOT NULL,
  `Fint1` bigint(20) DEFAULT NULL,
  `Fchar1` varchar(64) DEFAULT NULL,
  `Fdate1` datetime DEFAULT NULL,
  `Fsrc_info` text,
  `Fext_info` text,
  `Flast_update_time` datetime NOT NULL,
  PRIMARY KEY (`Fsrc_no`,`Flottery_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `t_lottery_draw_result` (
  `Flottery_id` varchar(32) NOT NULL,
  `Fissue_no` varchar(64) NOT NULL,
  `Fsrc_no` varchar(32) NOT NULL,
  `Fdraw_result` varchar(128) NOT NULL,
  `Fstate` int(11) NOT NULL DEFAULT '1',
  `Fpriority` int(11) NOT NULL DEFAULT '0',
  `Fcreate_time` datetime NOT NULL,
  `Fint1` bigint(20) DEFAULT NULL,
  `Fint2` bigint(20) DEFAULT NULL,
  `Fchar1` varchar(64) DEFAULT NULL,
  `Fchar2` varchar(64) DEFAULT NULL,
  `Fdate1` datetime DEFAULT NULL,
  `Fdate2` datetime DEFAULT NULL,
  `Fdraw_info` text,
  `Fext_info` text,
  `Flast_update_time` datetime NOT NULL,
  `Fstatus` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`Flottery_id`,`Fissue_no`,`Fsrc_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO cqfcdb.`t_lottery_draw_src` VALUES ('500', 'QLC', 'QLC:500Íò', 1, 0, '2014-11-14 10:51:57', NULL, NULL, NULL, NULL, NULL, '2014-11-14 10:52:02');
INSERT INTO cqfcdb.`t_lottery_draw_src` VALUES ('500', 'SSQ', 'SSQ:500Íò', 1, 0, '2014-11-14 10:50:52', NULL, NULL, NULL, NULL, NULL, '2014-11-14 10:51:07');

