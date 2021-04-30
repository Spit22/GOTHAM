-- MySQL dump 10.17  Distrib 10.3.25-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: GOTHAM
-- ------------------------------------------------------
-- Server version       10.3.25-MariaDB-0+deb10u1


--
-- Table structure for table `Honeypot`
--
DROP TABLE IF EXISTS `Honeypot`;
CREATE TABLE `Honeypot` (
  `id` varchar(35) NOT NULL,
  `name` varchar(128) NOT NULL,
  `descr` text DEFAULT NULL,
  `port` int(5) DEFAULT NULL,
  `parser` text NOT NULL,
  `logs` varchar(255) NOT NULL,
  `source` varchar(255) NOT NULL,
  `port_container` int(5) NOT NULL,
  `state` varchar(10) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `port` (`port`)
);

--
-- Table structure for table `Link`
--
DROP TABLE IF EXISTS `Link`;
CREATE TABLE `Link` (
  `id` varchar(35) NOT NULL,
  `nb_hp` int(5) NOT NULL,
  `nb_serv` int(5) NOT NULL,
  `ports` varchar(128) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
);

--
-- Table structure for table `Server`
--
DROP TABLE IF EXISTS `Server`;
CREATE TABLE `Server` (
  `id` varchar(35) NOT NULL,
  `name` varchar(128) NOT NULL,
  `descr` text DEFAULT NULL,
  `ip` varchar(15) NOT NULL,
  `ssh_key` text NOT NULL,
  `ssh_port` int(5) NOT NULL DEFAULT 22,
  `state` varchar(10) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `ip` (`ip`)
);

--
-- Table structure for table `Tags`
--
DROP TABLE IF EXISTS `Tags`;
CREATE TABLE `Tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(128) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `tag` (`tag`)
);

--
-- Table structure for table `Hp_Tags`
--
DROP TABLE IF EXISTS `Hp_Tags`;
CREATE TABLE `Hp_Tags` (
  `id_tag` int(11) NOT NULL,
  `id_hp` varchar(35) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_tag`,`id_hp`),
  KEY `id_hp` (`id_hp`),
  CONSTRAINT `Hp_Tags_ibfk_1` FOREIGN KEY (`id_tag`) REFERENCES `Tags` (`id`),
  CONSTRAINT `Hp_Tags_ibfk_2` FOREIGN KEY (`id_hp`) REFERENCES `Honeypot` (`id`)
);

--
-- Table structure for table `Serv_Tags`
--
DROP TABLE IF EXISTS `Serv_Tags`;
CREATE TABLE `Serv_Tags` (
  `id_tag` int(11) NOT NULL,
  `id_serv` varchar(35) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_tag`,`id_serv`),
  KEY `id_serv` (`id_serv`),
  CONSTRAINT `Serv_Tags_ibfk_1` FOREIGN KEY (`id_tag`) REFERENCES `Tags` (`id`),
  CONSTRAINT `Serv_Tags_ibfk_2` FOREIGN KEY (`id_serv`) REFERENCES `Server` (`id`)
);

--
-- Table structure for table `Link_Tags_hp`
--
DROP TABLE IF EXISTS `Link_Tags_hp`;
CREATE TABLE `Link_Tags_hp` (
  `id_tag` int(11) NOT NULL,
  `id_link` varchar(35) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_tag`,`id_link`),
  KEY `id_link` (`id_link`),
  CONSTRAINT `Link_Tags_hp_ibfk_1` FOREIGN KEY (`id_tag`) REFERENCES `Tags` (`id`),
  CONSTRAINT `Link_Tags_hp_ibfk_2` FOREIGN KEY (`id_link`) REFERENCES `Link` (`id`)
);

--
-- Table structure for table `Link_Tags_serv`
--
DROP TABLE IF EXISTS `Link_Tags_serv`;
CREATE TABLE `Link_Tags_serv` (
  `id_tag` int(11) NOT NULL,
  `id_link` varchar(35) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_tag`,`id_link`),
  KEY `id_link` (`id_link`),
  CONSTRAINT `Link_Tags_serv_ibfk_1` FOREIGN KEY (`id_tag`) REFERENCES `Tags` (`id`),
  CONSTRAINT `Link_Tags_serv_ibfk_2` FOREIGN KEY (`id_link`) REFERENCES `Link` (`id`)
);

--
-- Table structure for table `Link_Hp_Serv`
--
DROP TABLE IF EXISTS `Link_Hp_Serv`;
CREATE TABLE `Link_Hp_Serv` (
  `id_link` varchar(35) NOT NULL,
  `id_hp` varchar(35) NOT NULL,
  `id_serv` varchar(35) NOT NULL,
  `port` int(5) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_link`,`id_hp`,`id_serv`),
  KEY `id_hp` (`id_hp`),
  KEY `id_serv` (`id_serv`),
  CONSTRAINT `Link_Hp_Serv_ibfk_1` FOREIGN KEY (`id_link`) REFERENCES `Link` (`id`),
  CONSTRAINT `Link_Hp_Serv_ibfk_2` FOREIGN KEY (`id_hp`) REFERENCES `Honeypot` (`id`),
  CONSTRAINT `Link_Hp_Serv_ibfk_3` FOREIGN KEY (`id_serv`) REFERENCES `Server` (`id`)
);

--
-- Final view structure for view `view_hp`
--
CREATE VIEW `view_hp` AS 
select 
  `Honeypot`.`id` AS `id`,
  `Honeypot`.`name` AS `name`,
  `Honeypot`.`descr` AS `descr`,
  `Honeypot`.`port` AS `port`,
  `Honeypot`.`parser` AS `parser`,
  `Honeypot`.`logs` AS `logs`,
  `Honeypot`.`source` AS `source`,
  `Honeypot`.`state` AS `state`,
  `Honeypot`.`port_container` AS `port_container`,
  group_concat(distinct `Tags`.`tag` separator '||') AS `tags`,
  `Honeypot`.`created_at` AS `created_at`,
  `Honeypot`.`updated_at` AS `updated_at` 
from (
  (
    `Honeypot` 
    left join `Hp_Tags` 
    on(`Honeypot`.`id` = `Hp_Tags`.`id_hp`)
  ) 
  left join `Tags` 
  on(`Hp_Tags`.`id_tag` = `Tags`.`id`)
) group by `Honeypot`.`id`;

--
-- Final view structure for view `view_serv`
--
CREATE VIEW `view_serv` AS 
select 
  `Server`.`id` AS `id`,
  `Server`.`name` AS `name`,
  `Server`.`descr` AS `descr`,
  `Server`.`ip` AS `ip`,
  `Server`.`ssh_key` AS `ssh_key`,
  `Server`.`ssh_port` AS `ssh_port`,
  `Server`.`state` AS `state`,
  group_concat(distinct `Tags`.`tag` separator '||') AS `tags`,
  `Server`.`created_at` AS `created_at`,
  `Server`.`updated_at` AS `updated_at` 
from (
  (
    `Server` 
    left join `Serv_Tags` 
    on(`Server`.`id` = `Serv_Tags`.`id_serv`)
  ) 
  left join `Tags` 
  on(`Serv_Tags`.`id_tag` = `Tags`.`id`)
) group by `Server`.`id`;

--
-- Final view structure for view `view_link_hp`
--
CREATE VIEW `view_link_hp` AS 
select 
  `Link`.`id` AS `id`,
  `Link`.`nb_hp` AS `nb_hp`,
  `Link`.`nb_serv` AS `nb_serv`,
  `Link`.`ports` AS `ports`,
  group_concat(distinct `Tags`.`tag` separator '||') AS `tags_hp`,
  `Link`.`created_at` AS `created_at`,
  `Link`.`updated_at` AS `updated_at`
from (
  (
    `Link`
    left join `Link_Tags_hp` 
    on(`Link`.`id` = `Link_Tags_hp`.`id_link`)
  ) 
  left join `Tags` 
  on(`Link_Tags_hp`.`id_tag` = `Tags`.`id`)
) group by `Link`.`id`;

--
-- Final view structure for view `view_link_serv`
--
CREATE VIEW `view_link_serv` AS 
select 
  `Link`.`id` AS `id`,
  `Link`.`nb_hp` AS `nb_hp`,
  `Link`.`nb_serv` AS `nb_serv`,
  `Link`.`ports` AS `ports`,
  group_concat(distinct `Tags`.`tag` separator '||') AS `tags_serv`,
  `Link`.`created_at` AS `created_at`,
  `Link`.`updated_at` AS `updated_at`
from (
  (
    `Link` 
    left join `Link_Tags_serv` 
    on(`Link`.`id` = `Link_Tags_serv`.`id_link`)
  ) 
  left join `Tags` 
  on(`Link_Tags_serv`.`id_tag` = `Tags`.`id`)
) group by `Link`.`id`;

--
-- Final view structure for view `view_link`
--
CREATE VIEW `view_link` AS 
select 
  `view_link_hp`.`id` AS `id`,
  `view_link_hp`.`nb_hp` AS `nb_hp`,
  `view_link_hp`.`nb_serv` AS `nb_serv`,
  `view_link_hp`.`ports` AS `ports`,
  `view_link_hp`.`tags_hp` AS `tags_hp`,
  `view_link_serv`.`tags_serv` AS `tags_serv`,
  `view_link_hp`.`created_at` AS `created_at`,
  `view_link_hp`.`updated_at` AS `updated_at`
from (
  `view_link_hp` 
  join `view_link_serv` 
  on(`view_link_hp`.`id` = `view_link_serv`.`id`)
);

--
-- Final view structure for view `v_hp_full`
--
CREATE VIEW `v_hp_full` AS 
select 
  `v`.`hp_id` AS `hp_id`,
  `v`.`hp_name` AS `hp_name`,
  `v`.`hp_descr` AS `hp_descr`,
  `v`.`hp_port` AS `hp_port`,
  `v`.`hp_parser` AS `hp_parser`,
  `v`.`hp_logs` AS `hp_logs`,
  `v`.`hp_source` AS `hp_source`,
  `v`.`hp_state` AS `hp_state`,
  `v`.`hp_port_container` AS `hp_port_container`,
  `v`.`hp_tags` AS `hp_tags`,
  `v`.`hp_created_at` AS `hp_created_at`,
  `v`.`hp_updated_at` AS `hp_updated_at`,
  group_concat(IFNULL(`v`.`link_id`,'NULL') separator '||||||') AS `link_id`,
  group_concat(IFNULL(`v`.`link_nb_hp`,'NULL') separator '||||||') AS `link_nb_hp`,
  group_concat(IFNULL(`v`.`link_nb_serv`,'NULL') separator '||||||') AS `link_nb_serv`,
  group_concat(IFNULL(`v`.`link_ports`,'NULL') separator '||||||') AS `link_ports`,
  group_concat(IFNULL(`v`.`link_tags_hp`,'NULL') separator '||||||') AS `link_tags_hp`,
  group_concat(IFNULL(`v`.`link_tags_serv`,'NULL') separator '||||||') AS `link_tags_serv`,
  group_concat(IFNULL(`v`.`link_created_at`,'NULL') separator '||||||') AS `link_created_at`,
  group_concat(IFNULL(`v`.`link_updated_at`,'NULL') separator '||||||') AS `link_updated_at`,
  group_concat(IFNULL(`v`.`lhs_port`,'NULL') separator '||||||') AS `lhs_port`,
  group_concat(IFNULL(`v`.`serv_id`,'NULL') separator '||||||') AS `serv_id`,
  group_concat(IFNULL(`v`.`serv_name`,'NULL') separator '||||||') AS `serv_name`,
  group_concat(IFNULL(`v`.`serv_descr`,'NULL') separator '||||||') AS `serv_descr`,
  group_concat(IFNULL(`v`.`serv_ip`,'NULL') separator '||||||') AS `serv_ip`,
  group_concat(IFNULL(`v`.`serv_ssh_key`,'NULL') separator '||||||') AS `serv_ssh_key`,
  group_concat(IFNULL(`v`.`serv_ssh_port`,'NULL') separator '||||||') AS `serv_ssh_port`,
  group_concat(IFNULL(`v`.`serv_state`,'NULL') separator '||||||') AS `serv_state`,
  group_concat(IFNULL(`v`.`serv_tags`,'NULL') separator '||||||') AS `serv_tags`,
  group_concat(IFNULL(`v`.`serv_created_at`,'NULL') separator '||||||') AS `serv_created_at`,
  group_concat(IFNULL(`v`.`serv_updated_at`,'NULL') separator '||||||') AS `serv_updated_at` 
from (
  select 
    `view_hp`.`id` AS `hp_id`,
    `view_hp`.`name` AS `hp_name`,
    `view_hp`.`descr` AS `hp_descr`,
    `view_hp`.`port` AS `hp_port`,
    `view_hp`.`parser` AS `hp_parser`,
    `view_hp`.`logs` AS `hp_logs`,
    `view_hp`.`source` AS `hp_source`,
    `view_hp`.`state` AS `hp_state`,
    `view_hp`.`port_container` AS `hp_port_container`,
    `view_hp`.`tags` AS `hp_tags`,
    `view_hp`.`created_at` AS `hp_created_at`,
    `view_hp`.`updated_at` AS `hp_updated_at`,
    `view_link`.`id` AS `link_id`,
    `view_link`.`nb_hp` AS `link_nb_hp`,
    `view_link`.`nb_serv` AS `link_nb_serv`,
    `view_link`.`ports` AS `link_ports`,
    `view_link`.`tags_hp` AS `link_tags_hp`,
    `view_link`.`tags_serv` AS `link_tags_serv`,
    `view_link`.`created_at` AS `link_created_at`,
    `view_link`.`updated_at` AS `link_updated_at`,
    group_concat(IFNULL(`Link_Hp_Serv`.`port`,'NULL') separator '||||') AS `lhs_port`,
    group_concat(IFNULL(`view_serv`.`id`,'NULL') separator '||||') AS `serv_id`,
    group_concat(IFNULL(`view_serv`.`name`,'NULL') separator '||||') AS `serv_name`,
    group_concat(IFNULL(`view_serv`.`descr`,'NULL') separator '||||') AS `serv_descr`,
    group_concat(IFNULL(`view_serv`.`ip`,'NULL') separator '||||') AS `serv_ip`,
    group_concat(IFNULL(`view_serv`.`ssh_key`,'NULL') separator '||||') AS `serv_ssh_key`,
    group_concat(IFNULL(`view_serv`.`ssh_port`,'NULL') separator '||||') AS `serv_ssh_port`,
    group_concat(IFNULL(`view_serv`.`state`,'NULL') separator '||||') AS `serv_state`,
    group_concat(IFNULL(`view_serv`.`tags`,'NULL') separator '||||') AS `serv_tags`,
    group_concat(IFNULL(`view_serv`.`created_at`,'NULL') separator '||||') AS `serv_created_at`,
    group_concat(IFNULL(`view_serv`.`updated_at`,'NULL') separator '||||') AS `serv_updated_at` 
  from (
    (
      (
        `view_hp` 
        left join `Link_Hp_Serv` 
        on(`view_hp`.`id` = `Link_Hp_Serv`.`id_hp`)
      ) 
      left join `view_serv` 
      on(`Link_Hp_Serv`.`id_serv` = `view_serv`.`id`)
    ) 
    left join `view_link` on(`view_link`.`id` = `Link_Hp_Serv`.`id_link`)
  ) group by `view_hp`.`id`,`view_link`.`id`
) `v` 
group by `v`.`hp_id`;

--
-- Final view structure for view `v_serv_full`
--
CREATE VIEW `v_serv_full` AS 
select 
  `v`.`serv_id` AS `serv_id`,
  `v`.`serv_name` AS `serv_name`,
  `v`.`serv_descr` AS `serv_descr`,
  `v`.`serv_ip` AS `serv_ip`,
  `v`.`serv_ssh_key` AS `serv_ssh_key`,
  `v`.`serv_ssh_port` AS `serv_ssh_port`,
  `v`.`serv_state` AS `serv_state`,
  `v`.`serv_tags` AS `serv_tags`,
  `v`.`serv_created_at` AS `serv_created_at`,
  `v`.`serv_updated_at` AS `serv_updated_at`,
  group_concat(IFNULL(`v`.`link_id`,'NULL') separator '||||||') AS `link_id`,
  group_concat(IFNULL(`v`.`link_nb_hp`,'NULL') separator '||||||') AS `link_nb_hp`,
  group_concat(IFNULL(`v`.`link_nb_serv`,'NULL') separator '||||||') AS `link_nb_serv`,
  group_concat(IFNULL(`v`.`link_ports`,'NULL') separator '||||||') AS `link_ports`,
  group_concat(IFNULL(`v`.`link_tags_hp`,'NULL') separator '||||||') AS `link_tags_hp`,
  group_concat(IFNULL(`v`.`link_tags_serv`,'NULL') separator '||||||') AS `link_tags_serv`,
  group_concat(IFNULL(`v`.`link_created_at`,'NULL') separator '||||||') AS `link_created_at`,
  group_concat(IFNULL(`v`.`link_updated_at`,'NULL') separator '||||||') AS `link_updated_at`,
  group_concat(IFNULL(`v`.`lhs_port`,'NULL') separator '||||||') AS `lhs_port`,
  group_concat(IFNULL(`v`.`hp_id`,'NULL') separator '||||||') AS `hp_id`,
  group_concat(IFNULL(`v`.`hp_name`,'NULL') separator '||||||') AS `hp_name`,
  group_concat(IFNULL(`v`.`hp_descr`,'NULL') separator '||||||') AS `hp_descr`,
  group_concat(IFNULL(`v`.`hp_port`,'NULL') separator '||||||') AS `hp_port`,
  group_concat(IFNULL(`v`.`hp_parser`,'NULL') separator '||||||') AS `hp_parser`,
  group_concat(IFNULL(`v`.`hp_logs`,'NULL') separator '||||||') AS `hp_logs`,
  group_concat(IFNULL(`v`.`hp_source`,'NULL') separator '||||||') AS `hp_source`,
  group_concat(IFNULL(`v`.`hp_state`,'NULL') separator '||||||') AS `hp_state`,
  group_concat(IFNULL(`v`.`hp_port_container`,'NULL') separator '||||||') AS `hp_port_container`,
  group_concat(IFNULL(`v`.`hp_tags`,'NULL') separator '||||||') AS `hp_tags`,
  group_concat(IFNULL(`v`.`hp_created_at`,'NULL') separator '||||||') AS `hp_created_at`,
  group_concat(IFNULL(`v`.`hp_updated_at`,'NULL') separator '||||||') AS `hp_updated_at` 
from (
  select 
    `view_serv`.`id` AS `serv_id`,
    `view_serv`.`name` AS `serv_name`,
    `view_serv`.`descr` AS `serv_descr`,
    `view_serv`.`ip` AS `serv_ip`,
    `view_serv`.`ssh_key` AS `serv_ssh_key`,
    `view_serv`.`ssh_port` AS `serv_ssh_port`,
    `view_serv`.`state` AS `serv_state`,
    `view_serv`.`tags` AS `serv_tags`,
    `view_serv`.`created_at` AS `serv_created_at`,
    `view_serv`.`updated_at` AS `serv_updated_at`,
    `view_link`.`id` AS `link_id`,
    `view_link`.`nb_hp` AS `link_nb_hp`,
    `view_link`.`nb_serv` AS `link_nb_serv`,
    `view_link`.`ports` AS `link_ports`,
    `view_link`.`tags_hp` AS `link_tags_hp`,
    `view_link`.`tags_serv` AS `link_tags_serv`,
    `view_link`.`created_at` AS `link_created_at`,
    `view_link`.`updated_at` AS `link_updated_at`,
    group_concat(IFNULL(`Link_Hp_Serv`.`port`,'NULL') separator '||||') AS `lhs_port`,
    group_concat(IFNULL(`view_hp`.`id`,'NULL') separator '||||') AS `hp_id`,
    group_concat(IFNULL(`view_hp`.`name`,'NULL') separator '||||') AS `hp_name`,
    group_concat(IFNULL(`view_hp`.`descr`,'NULL') separator '||||') AS `hp_descr`,
    group_concat(IFNULL(`view_hp`.`port`,'NULL') separator '||||') AS `hp_port`,
    group_concat(IFNULL(`view_hp`.`parser`,'NULL') separator '||||') AS `hp_parser`,
    group_concat(IFNULL(`view_hp`.`logs`,'NULL') separator '||||') AS `hp_logs`,
    group_concat(IFNULL(`view_hp`.`source`,'NULL') separator '||||') AS `hp_source`,
    group_concat(IFNULL(`view_hp`.`state`,'NULL') separator '||||') AS `hp_state`,
    group_concat(IFNULL(`view_hp`.`port_container`,'NULL') separator '||||') AS `hp_port_container`,
    group_concat(IFNULL(`view_hp`.`tags`,'NULL') separator '||||') AS `hp_tags`,
    group_concat(IFNULL(`view_hp`.`created_at`,'NULL') separator '||||') AS `hp_created_at`,
    group_concat(IFNULL(`view_hp`.`updated_at`,'NULL') separator '||||') AS `hp_updated_at` 
  from (
    (
      (
        `view_serv` 
        left join `Link_Hp_Serv` 
        on(`view_serv`.`id` = `Link_Hp_Serv`.`id_serv`)
      ) 
      left join `view_hp` 
      on(`Link_Hp_Serv`.`id_hp` = `view_hp`.`id`)
    ) 
    left join `view_link` 
    on(`view_link`.`id` = `Link_Hp_Serv`.`id_link`)
  ) group by `view_serv`.`id`,`view_link`.`id`
) `v` 
group by `v`.`serv_id`;

--
-- Final view structure for view `v_link_full_hp_serv`
--
CREATE VIEW `v_link_full_hp_serv` AS 
select 
  `v`.`link_id` AS `link_id`,
  `v`.`link_nb_hp` AS `link_nb_hp`,
  `v`.`link_nb_serv` AS `link_nb_serv`,
  `v`.`link_ports` AS `link_ports`,
  `v`.`link_tags_hp` AS `link_tags_hp`,
  `v`.`link_tags_serv` AS `link_tags_serv`,
  `v`.`link_created_at` AS `link_created_at`,
  `v`.`link_updated_at` AS `link_updated_at`,
  group_concat(IFNULL(`v`.`hp_id`,'NULL') separator '||||||') AS `hp_id`,
  group_concat(IFNULL(`v`.`hp_name`,'NULL') separator '||||||') AS `hp_name`,
  group_concat(IFNULL(`v`.`hp_descr`,'NULL') separator '||||||') AS `hp_descr`,
  group_concat(IFNULL(`v`.`hp_port`,'NULL') separator '||||||') AS `hp_port`,
  group_concat(IFNULL(`v`.`hp_parser`,'NULL') separator '||||||') AS `hp_parser`,
  group_concat(IFNULL(`v`.`hp_logs`,'NULL') separator '||||||') AS `hp_logs`,
  group_concat(IFNULL(`v`.`hp_source`,'NULL') separator '||||||') AS `hp_source`,
  group_concat(IFNULL(`v`.`hp_state`,'NULL') separator '||||||') AS `hp_state`,
  group_concat(IFNULL(`v`.`hp_port_container`,'NULL') separator '||||||') AS `hp_port_container`,
  group_concat(IFNULL(`v`.`hp_tags`,'NULL') separator '||||||') AS `hp_tags`,
  group_concat(IFNULL(`v`.`hp_created_at`,'NULL') separator '||||||') AS `hp_created_at`,
  group_concat(IFNULL(`v`.`hp_updated_at`,'NULL') separator '||||||') AS `hp_updated_at`,
  group_concat(IFNULL(`v`.`lhs_port`,'NULL') separator '||||||') AS `lhs_port`,
  group_concat(IFNULL(`v`.`serv_id`,'NULL') separator '||||||') AS `serv_id`,
  group_concat(IFNULL(`v`.`serv_name`,'NULL') separator '||||||') AS `serv_name`,
  group_concat(IFNULL(`v`.`serv_descr`,'NULL') separator '||||||') AS `serv_descr`,
  group_concat(IFNULL(`v`.`serv_ip`,'NULL') separator '||||||') AS `serv_ip`,
  group_concat(IFNULL(`v`.`serv_ssh_key`,'NULL') separator '||||||') AS `serv_ssh_key`,
  group_concat(IFNULL(`v`.`serv_ssh_port`,'NULL') separator '||||||') AS `serv_ssh_port`,
  group_concat(IFNULL(`v`.`serv_state`,'NULL') separator '||||||') AS `serv_state`,
  group_concat(IFNULL(`v`.`serv_tags`,'NULL') separator '||||||') AS `serv_tags`,
  group_concat(IFNULL(`v`.`serv_created_at`,'NULL') separator '||||||') AS `serv_created_at`,
  group_concat(IFNULL(`v`.`serv_updated_at`,'NULL') separator '||||||') AS `serv_updated_at` 
from (
  select 
    `view_link`.`id` AS `link_id`,
    `view_link`.`nb_hp` AS `link_nb_hp`,
    `view_link`.`nb_serv` AS `link_nb_serv`,
    `view_link`.`ports` AS `link_ports`,
    `view_link`.`tags_hp` AS `link_tags_hp`,
    `view_link`.`tags_serv` AS `link_tags_serv`,
    `view_link`.`created_at` AS `link_created_at`,
    `view_link`.`updated_at` AS `link_updated_at`,
    `view_hp`.`id` AS `hp_id`,`view_hp`.`name` AS `hp_name`,
    `view_hp`.`descr` AS `hp_descr`,
    `view_hp`.`port` AS `hp_port`,
    `view_hp`.`parser` AS `hp_parser`,
    `view_hp`.`logs` AS `hp_logs`,
    `view_hp`.`source` AS `hp_source`,
    `view_hp`.`state` AS `hp_state`,
    `view_hp`.`port_container` AS `hp_port_container`,
    `view_hp`.`tags` AS `hp_tags`,
    `view_hp`.`created_at` AS `hp_created_at`,
    `view_hp`.`updated_at` AS `hp_updated_at`,
    group_concat(IFNULL(`Link_Hp_Serv`.`port`,'NULL') separator '||||') AS `lhs_port`,
    group_concat(IFNULL(`view_serv`.`id`,'NULL') separator '||||') AS `serv_id`,
    group_concat(IFNULL(`view_serv`.`name`,'NULL') separator '||||') AS `serv_name`,
    group_concat(IFNULL(`view_serv`.`descr`,'NULL') separator '||||') AS `serv_descr`,
    group_concat(IFNULL(`view_serv`.`ip`,'NULL') separator '||||') AS `serv_ip`,
    group_concat(IFNULL(`view_serv`.`ssh_key`,'NULL') separator '||||') AS `serv_ssh_key`,
    group_concat(IFNULL(`view_serv`.`ssh_port`,'NULL') separator '||||') AS `serv_ssh_port`,
    group_concat(IFNULL(`view_serv`.`state`,'NULL') separator '||||') AS `serv_state`,
    group_concat(IFNULL(`view_serv`.`tags`,'NULL') separator '||||') AS `serv_tags`,
    group_concat(IFNULL(`view_serv`.`created_at`,'NULL') separator '||||') AS `serv_created_at`,
    group_concat(IFNULL(`view_serv`.`updated_at`,'NULL') separator '||||') AS `serv_updated_at` 
  from (
    (
      (
        `view_link` 
        left join `Link_Hp_Serv` 
        on(`view_link`.`id` = `Link_Hp_Serv`.`id_link`)
      ) 
      left join `view_serv` 
      on(`Link_Hp_Serv`.`id_serv` = `view_serv`.`id`)
    ) 
    left join `view_hp` 
    on(`view_hp`.`id` = `Link_Hp_Serv`.`id_hp`)
  ) group by `view_hp`.`id`,`view_link`.`id`
) `v` 
group by `v`.`link_id`;

--
-- Final view structure for view `v_link_full_serv_hp`
--
CREATE VIEW `v_link_full_serv_hp` AS 
select 
  `v`.`link_id` AS `link_id`,
  `v`.`link_nb_hp` AS `link_nb_hp`,
  `v`.`link_nb_serv` AS `link_nb_serv`,
  `v`.`link_ports` AS `link_ports`,
  `v`.`link_tags_hp` AS `link_tags_hp`,
  `v`.`link_tags_serv` AS `link_tags_serv`,
  `v`.`link_created_at` AS `link_created_at`,
  `v`.`link_updated_at` AS `link_updated_at`,
  group_concat(IFNULL(`v`.`serv_id`,'NULL') separator '||||||') AS `serv_id`,
  group_concat(IFNULL(`v`.`serv_name`,'NULL') separator '||||||') AS `serv_name`,
  group_concat(IFNULL(`v`.`serv_descr`,'NULL') separator '||||||') AS `serv_descr`,
  group_concat(IFNULL(`v`.`serv_ip`,'NULL') separator '||||||') AS `serv_ip`,
  group_concat(IFNULL(`v`.`serv_ssh_key`,'NULL') separator '||||||') AS `serv_ssh_key`,
  group_concat(IFNULL(`v`.`serv_ssh_port`,'NULL') separator '||||||') AS `serv_ssh_port`,
  group_concat(IFNULL(`v`.`serv_state`,'NULL') separator '||||||') AS `serv_state`,
  group_concat(IFNULL(`v`.`serv_tags`,'NULL') separator '||||||') AS `serv_tags`,
  group_concat(IFNULL(`v`.`serv_created_at`,'NULL') separator '||||||') AS `serv_created_at`,
  group_concat(IFNULL(`v`.`serv_updated_at`,'NULL') separator '||||||') AS `serv_updated_at`,
  group_concat(IFNULL(`v`.`lhs_port`,'NULL') separator '||||||') AS `lhs_port`,
  group_concat(IFNULL(`v`.`hp_id`,'NULL') separator '||||||') AS `hp_id`,
  group_concat(IFNULL(`v`.`hp_name`,'NULL') separator '||||||') AS `hp_name`,
  group_concat(IFNULL(`v`.`hp_descr`,'NULL') separator '||||||') AS `hp_descr`,
  group_concat(IFNULL(`v`.`hp_port`,'NULL') separator '||||||') AS `hp_port`,
  group_concat(IFNULL(`v`.`hp_parser`,'NULL') separator '||||||') AS `hp_parser`,
  group_concat(IFNULL(`v`.`hp_logs`,'NULL') separator '||||||') AS `hp_logs`,
  group_concat(IFNULL(`v`.`hp_source`,'NULL') separator '||||||') AS `hp_source`,
  group_concat(IFNULL(`v`.`hp_state`,'NULL') separator '||||||') AS `hp_state`,
  group_concat(IFNULL(`v`.`hp_port_container`,'NULL') separator '||||||') AS `hp_port_container`,
  group_concat(IFNULL(`v`.`hp_tags`,'NULL') separator '||||||') AS `hp_tags`,
  group_concat(IFNULL(`v`.`hp_created_at`,'NULL') separator '||||||') AS `hp_created_at`,
  group_concat(IFNULL(`v`.`hp_updated_at`,'NULL') separator '||||||') AS `hp_updated_at` 
from (
  select 
    `view_link`.`id` AS `link_id`,
    `view_link`.`nb_hp` AS `link_nb_hp`,
    `view_link`.`nb_serv` AS `link_nb_serv`,
    `view_link`.`ports` AS `link_ports`,
    `view_link`.`tags_hp` AS `link_tags_hp`,
    `view_link`.`tags_serv` AS `link_tags_serv`,
    `view_link`.`created_at` AS `link_created_at`,
    `view_link`.`updated_at` AS `link_updated_at`,
    `view_serv`.`id` AS `serv_id`,
    `view_serv`.`name` AS `serv_name`,
    `view_serv`.`descr` AS `serv_descr`,
    `view_serv`.`ip` AS `serv_ip`,
    `view_serv`.`ssh_key` AS `serv_ssh_key`,
    `view_serv`.`ssh_port` AS `serv_ssh_port`,
    `view_serv`.`state` AS `serv_state`,
    `view_serv`.`tags` AS `serv_tags`,
    `view_serv`.`created_at` AS `serv_created_at`,
    `view_serv`.`updated_at` AS `serv_updated_at`,
    group_concat(IFNULL(`Link_Hp_Serv`.`port`,'NULL') separator '||||') AS `lhs_port`,
    group_concat(IFNULL(`view_hp`.`id`,'NULL') separator '||||') AS `hp_id`,
    group_concat(IFNULL(`view_hp`.`name`,'NULL') separator '||||') AS `hp_name`,
    group_concat(IFNULL(`view_hp`.`descr`,'NULL') separator '||||') AS `hp_descr`,
    group_concat(IFNULL(`view_hp`.`port`,'NULL') separator '||||') AS `hp_port`,
    group_concat(IFNULL(`view_hp`.`parser`,'NULL') separator '||||') AS `hp_parser`,
    group_concat(IFNULL(`view_hp`.`logs`,'NULL') separator '||||') AS `hp_logs`,
    group_concat(IFNULL(`view_hp`.`source`,'NULL') separator '||||') AS `hp_source`,
    group_concat(IFNULL(`view_hp`.`state`,'NULL') separator '||||') AS `hp_state`,
    group_concat(IFNULL(`view_hp`.`port_container`,'NULL') separator '||||') AS `hp_port_container`,
    group_concat(IFNULL(`view_hp`.`tags`,'NULL') separator '||||') AS `hp_tags`,
    group_concat(IFNULL(`view_hp`.`created_at`,'NULL') separator '||||') AS `hp_created_at`,
    group_concat(IFNULL(`view_hp`.`updated_at`,'NULL') separator '||||') AS `hp_updated_at` 
  from (
    (
      (
        `view_link` 
        left join `Link_Hp_Serv` 
        on(`view_link`.`id` = `Link_Hp_Serv`.`id_link`)
      ) 
      left join `view_serv` 
      on(`Link_Hp_Serv`.`id_serv` = `view_serv`.`id`)
    ) 
    left join `view_hp` 
    on(`view_hp`.`id` = `Link_Hp_Serv`.`id_hp`)
  ) group by `view_serv`.`id`,`view_link`.`id`
) `v` 
group by `v`.`link_id`;

--
-- Final view structure for view `view_full`
--
CREATE VIEW `view_full` AS 
select 
  `view_hp`.`id` AS `hp_id`,
  `view_hp`.`name` AS `hp_name`,
  `view_hp`.`descr` AS `hp_descr`,
  `view_hp`.`port` AS `hp_port`,
  `view_hp`.`parser` AS `hp_parser`,
  `view_hp`.`logs` AS `hp_logs`,
  `view_hp`.`source` AS `hp_source`,
  `view_hp`.`state` AS `hp_state`,
  `view_hp`.`port_container` AS `hp_port_container`,
  `view_hp`.`tags` AS `hp_tags`,
  `view_hp`.`created_at` AS `hp_created_at`,
  `view_hp`.`updated_at` AS `hp_updated_at`,
  `view_link`.`id` AS `link_id`,
  `view_link`.`nb_hp` AS `link_nb_hp`,
  `view_link`.`nb_serv` AS `link_nb_serv`,
  `view_link`.`ports` AS `link_ports`,
  `view_link`.`tags_hp` AS `link_tags_hp`,
  `view_link`.`tags_serv` AS `link_tags_serv`,
  `view_link`.`created_at` AS `link_created_at`,
  `view_link`.`updated_at` AS `link_updated_at`,
  `view_serv`.`id` AS `serv_id`,
  `view_serv`.`name` AS `serv_name`,
  `view_serv`.`descr` AS `serv_descr`,
  `view_serv`.`ip` AS `serv_ip`,
  `view_serv`.`ssh_key` AS `serv_ssh_key`,
  `view_serv`.`ssh_port` AS `serv_ssh_port`,
  `view_serv`.`state` AS `serv_state`,
  `view_serv`.`tags` AS `serv_tags`,
  `view_serv`.`created_at` AS `serv_created_at`,
  `view_serv`.`updated_at` AS `serv_updated_at`,
  `Link_Hp_Serv`.`port` AS `lhs_port` 
from (
  (
    (
      `view_hp` 
      left join `Link_Hp_Serv` 
      on(`view_hp`.`id` = `Link_Hp_Serv`.`id_hp`)
    ) 
    left join `view_serv` 
    on(`Link_Hp_Serv`.`id_serv` = `view_serv`.`id`)
  ) 
  left join `view_link` 
  on(`view_link`.`id` = `Link_Hp_Serv`.`id_link`)
) 
union 
select 
  `view_hp`.`id` AS `hp_id`,
  `view_hp`.`name` AS `hp_name`,
  `view_hp`.`descr` AS `hp_descr`,
  `view_hp`.`port` AS `hp_port`,
  `view_hp`.`parser` AS `hp_parser`,
  `view_hp`.`logs` AS `hp_logs`,
  `view_hp`.`source` AS `hp_source`,
  `view_hp`.`state` AS `hp_state`,
  `view_hp`.`port_container` AS `hp_port_container`,
  `view_hp`.`tags` AS `hp_tags`,
  `view_hp`.`created_at` AS `hp_created_at`,
  `view_hp`.`updated_at` AS `hp_updated_at`,
  `view_link`.`id` AS `link_id`,
  `view_link`.`nb_hp` AS `link_nb_hp`,
  `view_link`.`nb_serv` AS `link_nb_serv`,
  `view_link`.`ports` AS `link_ports`,
  `view_link`.`tags_hp` AS `link_tags_hp`,
  `view_link`.`tags_serv` AS `link_tags_serv`,
  `view_link`.`created_at` AS `link_created_at`,
  `view_link`.`updated_at` AS `link_updated_at`,
  `view_serv`.`id` AS `serv_id`,
  `view_serv`.`name` AS `serv_name`,
  `view_serv`.`descr` AS `serv_descr`,
  `view_serv`.`ip` AS `serv_ip`,
  `view_serv`.`ssh_key` AS `serv_ssh_key`,
  `view_serv`.`ssh_port` AS `serv_ssh_port`,
  `view_serv`.`state` AS `serv_state`,
  `view_serv`.`tags` AS `serv_tags`,
  `view_serv`.`created_at` AS `serv_created_at`,
  `view_serv`.`updated_at` AS `serv_updated_at`,
  `Link_Hp_Serv`.`port` AS `lhs_port` 
from (
  (
    `view_serv` 
    left join (
      `Link_Hp_Serv` 
      left join `view_hp` 
      on(`view_hp`.`id` = `Link_Hp_Serv`.`id_hp`)
    ) 
    on(`Link_Hp_Serv`.`id_serv` = `view_serv`.`id`)
  ) 
  left join `view_link` 
  on(`view_link`.`id` = `Link_Hp_Serv`.`id_link`)
);
