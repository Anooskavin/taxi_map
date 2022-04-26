CREATE DATABASE `taxi_booking_app`;

DROP TABLE IF EXISTS `taxi_booking_app`.`users`;
CREATE TABLE  `taxi_booking_app`.`users` (
  `UID` int(11) NOT NULL AUTO_INCREMENT,
  `UNAME` varchar(50) NOT NULL,
  `EMAIL` varchar(50) NOT NULL,
  `UPASS` varchar(50) NOT NULL,
  `CONTACT` varchar(50) NOT NULL,
  PRIMARY KEY (`UID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE  `taxi_booking_app`.`driver` (
  `UID` int(11) NOT NULL AUTO_INCREMENT,
  `UNAME` varchar(50) NOT NULL,
  `EMAIL` varchar(50) NOT NULL,
  `UPASS` varchar(50) NOT NULL,
  `CONTACT` varchar(50) NOT NULL,
  PRIMARY KEY (`UID`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
SELECT *FROM `taxi_booking_app`.`users`;
SELECT *FROM `taxi_booking_app`.`driver`;