-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';



-- -----------------------------------------------------
-- Schema Worldway Travel
-- -----------------------------------------------------
-- drop schema if exists `Worldway Travel`;
-- create schema `Worldway Travel`;


-- -----------------------------------------------------
-- Schema Worldway Travel
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Order_Details`;
DROP TABLE IF EXISTS `Orders`;
DROP TABLE IF EXISTS `Messages`;
DROP TABLE IF EXISTS `Accounts`;
DROP TABLE IF EXISTS `Products`;
DROP TABLE IF EXISTS `SystemAdministrator`;
DROP TABLE IF EXISTS `Manager`;
DROP TABLE IF EXISTS `Staff`;
DROP TABLE IF EXISTS `Customer`;
DROP TABLE IF EXISTS `User`;
DROP TABLE IF EXISTS `Categories`;


-- -----------------------------------------------------
-- Table `User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `User` (
  `user_id` INT AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` VARCHAR(255) NOT NULL COMMENT '\'Role,  Customer,  Staff, Manager, SystemAdministrator\'',
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Customer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Customer` (
  `customer_id` INT NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `title` VARCHAR(255) NULL,
  `date_birth` DATE NULL,
  `email` VARCHAR(255) NULL,
  `phone_number` VARCHAR(20) NULL,
  `address` VARCHAR(255) NULL,
  `points_balance` INT NULL,
  `credit_limit` DECIMAL NULL,
  `remaining_credit` DECIMAL NULL,
  `image_url` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL COMMENT '\'Status, Active, Inactive\'',
  PRIMARY KEY (`customer_id`),
  CONSTRAINT `fk_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Staff`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Staff` (
  `staff_id` INT NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `title` VARCHAR(255) NULL,
  `date_join` DATE NULL,
  `email` VARCHAR(255) NULL,
  `phone_number` VARCHAR(255) NULL,
  `image_url` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL COMMENT '\'Status, Active,  Inactive\'',
  PRIMARY KEY (`staff_id`),
  CONSTRAINT `fk_staff_id`
    FOREIGN KEY (`staff_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Manager`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Manager` (
  `manager_id` INT NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `title` VARCHAR(255) NULL,
  `date_join` DATE NULL,
  `email` VARCHAR(255) NULL,
  `phone_number` VARCHAR(255) NULL,
  `image_url` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL COMMENT '\'Status, Avtive, Inactive\'',
  PRIMARY KEY (`manager_id`),
  CONSTRAINT `fk_manager_id`
    FOREIGN KEY (`manager_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `SystemAdministrator`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SystemAdministrator` (
  `admin_id` INT NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `title` VARCHAR(255) NULL,
  `date_join` DATE NULL,
  `email` VARCHAR(255) NULL,
  `phone_number` VARCHAR(255) NULL,
  `image_url` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL COMMENT '\'Status, Active, Inactive\'',
  PRIMARY KEY (`admin_id`),
  CONSTRAINT `fk_admin_id`
    FOREIGN KEY (`admin_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Categories` (
  `category_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `parent_category_id` INT NULL,
  PRIMARY KEY (`category_id`),
  INDEX `fk_parent_category_id_idx` (`parent_category_id` ASC) VISIBLE,
  CONSTRAINT `fk_parent_category_id`
    FOREIGN KEY (`parent_category_id`)
    REFERENCES `Categories` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `Products`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Products` (
  `product_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `category_id` INT NOT NULL,
  `price` DECIMAL(10,2) NULL,
  `description` TEXT NULL,
  `stock_level` INT NULL,
  `image_url` VARCHAR(255) NULL,
  `discount_details` VARCHAR(255) NULL,
  `status` VARCHAR(255) NOT NULL COMMENT '\'Status, Available, Unavailable\'',
  PRIMARY KEY (`product_id`),
  INDEX `fk_category_id_idx` (`category_id` ASC) VISIBLE,
  CONSTRAINT `fk_category_id`
    FOREIGN KEY (`category_id`)
    REFERENCES `Categories` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Orders`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Orders` (
  `order_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `order_date` DATE NULL,
  `total_cost` DECIMAL NULL,
  `status` VARCHAR(255) NULL COMMENT '\'Status, Pending, Progressing, Confirmed, Completed, Cancelled\'',
  `status_change_date`  DATETIME DEFAULT NULL COMMENT 'Date and time when the status was last updated',
  PRIMARY KEY (`order_id`),
  INDEX `fk_order_customer_id_idx` (`customer_id` ASC) VISIBLE,
  CONSTRAINT `fk_order_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `Customer` (`customer_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `Order_Details`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Order_Details` (
  `order_detail_id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `price` DECIMAL NULL,
  PRIMARY KEY (`order_detail_id`),
  INDEX `fk_orderdetail_order_id_idx` (`order_id` ASC) VISIBLE,
  INDEX `fk_orderdetail_product_id_idx` (`product_id` ASC) VISIBLE,
  CONSTRAINT `fk_orderdetail_order_id`
    FOREIGN KEY (`order_id`)
    REFERENCES `Orders` (`order_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_orderdetail_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `Products` (`product_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Accounts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Accounts` (
  `account_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `credit_limit` DECIMAL NOT NULL,
  `outstanding_balance` DECIMAL NOT NULL,
  `invoice_due_date` DATE NULL,
  `invoice_frequency` VARCHAR(255) NULL,
  PRIMARY KEY (`account_id`),
  INDEX `fk_accounts_customer_id_idx` (`customer_id` ASC) VISIBLE,
  CONSTRAINT `fk_accounts_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `Customer` (`customer_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Messages` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `sender_id` INT NOT NULL,
  `recipient_id` INT NOT NULL,
  `message_type` ENUM('standard', 'apply_credit', 'reply_credit', 'reply') DEFAULT 'standard',
  `message_content` TEXT NOT NULL,
  `message_date` DATETIME NOT NULL,
  `reply_status` ENUM('waiting for reply', 'replied') DEFAULT 'waiting for reply',
  PRIMARY KEY (`message_id`),
  INDEX `fk_message_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_message_receive_idx` (`recipient_id` ASC) VISIBLE,
  CONSTRAINT `fk_message`
    FOREIGN KEY (`sender_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_message_receive`
    FOREIGN KEY (`recipient_id`)
    REFERENCES `User` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

INSERT INTO `User` (`user_id`, `username`, `password`, `role`)
VALUES
    (1, 'customer1', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (2, 'customer2', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (3, 'customer3', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (4, 'customer4', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (5, 'customer5', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (6, 'customer6', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (7, 'customer7', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (8, 'customer8', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (9, 'customer9', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (10, 'customer10', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (11, 'customer11', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (12, 'customer12', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (13, 'customer13', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (14, 'customer14', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (15, 'customer15', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Customer'),
    (16, 'sales1', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (17, 'sales2', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (18, 'sales3', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (19, 'sales4', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (20, 'sales5', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (21, 'sales6', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (22, 'sales7', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (23, 'sales8', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (24, 'sales9', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (25, 'sales10', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Staff'),
    (26, 'marketing1', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'Manager'),
    (27, 'admin1', 'aa953a6d81c076a57dad53421b597a4527dcac3a95ba2d7d1e11ccabdd95acc3', 'SystemAdministrator');


INSERT INTO `Customer` 
(`customer_id`, `first_name`, `last_name`, `title`, `date_birth`, `email`, `phone_number`, `address`, `remaining_credit`, `image_url`, `status`)
VALUES 
(1, 'Joseph', 'Lewis', 'Mr', '1990-01-01', 'josephlewis@example.com', '0217893454', 'GI3345346834',  500.00, 'c1.jpg', 'Active'),
(2, 'Richard', 'Lee', 'Ms', '1985-05-15', 'richardlee@example.com', '0221362076', 'HA7245234634',  -1.00, 'c2.jpg', 'Active'),
(3, 'William', 'Lopez', 'Mr', '1978-09-30', 'williamlopez@example.com', '0223156788', 'HSDFG584936',  1000.00, 'c3.jpg', 'Inactive'),
(4, 'Thomas', 'Scott', 'Mr', '1988-05-14', 'thomasscott@example.com', '0223876396', 'QWET423563564Y', 950.00, 'c4.jpg', 'Active'),
(5, 'Paul', 'Brown', 'Mr', '1988-02-26', 'paulbrown@example.com', '0220467395', 'CVB91973',  400.00, 'c5.jpg', 'Active'),
(6, 'Matthew', 'Jackson', 'Mr', '1986-09-16', 'mattewjackson@example.com', '0221236393', 'UQD41453296',  100.00, 'c6.jpg', 'Active'),
(7, 'Mark', 'Allen', 'Mr', '1983-08-08', 'markallen@example.com', '0273646378', 'OQ8348937456',  300.00, 'c7.jpg', 'Active'),
(8, 'Linda', 'Walker', 'Miss', '1999-04-29', 'lindawalker@example.com', '0213646396', 'SDFHGJOI78569',  530.00, 'c8.jpg', 'Active'),
(9, 'Susan', 'Hall', 'Miss', '1998-12-23', 'susanhall@example.com', '0213606322', 'VM453745677',  20.00, 'c9.jpg', 'Active'),
(10, 'Jessica', 'King', 'Miss', '1999-05-16', 'jessicaking@example.com', '0213456318', 'OIT356475868',  -1.00, 'c10.jpg', 'Active'),
(11, 'Mary', 'Adams', 'Miss', '1997-01-17', 'maryadams@example.com', '0273680398', 'QS723424',  -1.00, 'c11.jpg', 'Active'),
(12, 'Sara', 'Baker', 'Ms', '1985-04-26', 'sarabaker@example.com', '0273046445', 'JST5246765',  -1.00, 'c12.jpg', 'Active'),
(13, 'Lisa', 'Moore', 'Ms', '1988-03-09', 'lisamoore@example.com', '0223635308', 'ERTW4564754',  -1.00, 'c13.jpg', 'Active'),
(14, 'Sandra', 'Nelson', 'Ms', '1983-07-11', 'sandranelson@example.com', '0221246308', 'JD6575743',  -1.00, 'c14.jpg', 'Active'),
(15, 'Carol', 'Wilson', 'Ms', '1982-11-03', 'carolwilson@example.com', '0223606388', 'IE3453643',  -1.00, 'c15.jpg', 'Active');



INSERT INTO `Staff` 
(`staff_id`, `first_name`, `last_name`, `title`, `date_join`, `email`, `phone_number`, `image_url`, `status`) 
VALUES 
(16, 'Anthony', 'Young', 'Mr', '2015-03-10', 'anthonyyoung@example.com', '0223052435', 's1.jpg', 'Active'),
(17, 'Nancy', 'Wilson', 'Ms', '2018-07-20', 'nancywilson@example.com', '0221231302', 's2.jpg', 'Active'),
(18, 'Sophia', 'Green', 'Ms', '2020-01-05', 'sophiagreen@example.com', '0220182037', 's3.jpg', 'Active'),
(19, 'David', 'Harris', 'Mr', '2015-03-10', 'davidharris@example.com', '0272202435', 's4.jpg', 'Active'),
(20, 'Ethan', 'White', 'Mr', '2018-07-20', 'ethanwhite@example.com', '0228805362', 's5.jpg', 'Active'),
(21, 'Lucas', 'Clark', 'Mr', '2020-01-05', 'lucasclark@example.com', '0210180037', 's6.jpg', 'Active'),
(22, 'Harper', 'Martin', 'Mr', '2015-03-10', 'harpermartin@example.com', '0223452455', 's7.jpg', 'Active'),
(23, 'Aidan', 'Perez', 'Mr', '2018-07-20', 'aidanperez@example.com', '0221885382', 's8.jpg', 'Active'),
(24, 'Ella', 'Anderson', 'Ms', '2020-01-05', 'ellaanderson@example.com', '0220182997', 's9.jpg', 'Active'),
(25, 'Zoe', 'Brooks', 'Ms', '2015-03-10', 'zoebrooks@example.com', '0270452335', 's10.jpg', 'Active');


INSERT INTO `Manager` 
(`manager_id`, `first_name`, `last_name`, `title`, `date_join`, `email`, `phone_number`, `image_url`, `status`) 
VALUES 
(26, 'David', 'Martinez', 'Mr', '2012-11-15', 'david.martinez@example.com', '0229844537', 'manager.jpg', 'Active');


INSERT INTO `SystemAdministrator` 
(`admin_id`, `first_name`, `last_name`, `title`, `date_join`, `email`, `phone_number`, `image_url`, `status`) 
VALUES 
(27, 'Olivia', 'Davis', 'Ms', '2014-06-25', 'olivia.davis@example.com', '0273546378', 'admin.jpg', 'Active');

INSERT INTO `Categories`
(`category_id`, `name`, `parent_category_id`)
VALUES


(1, 'CHINA', NULL),
(5, 'CHENG-DU', 1),
(6, 'XI-AN', 1),
(7, 'KUN-MING', 1),
(8, 'HANG-ZHOU', 1),
(9, 'SI-CHUAN', 1),
(10, 'SAN-XIA', 1),
(2, 'NEW-ZEALAND', NULL),
(11, 'SOUTH-ISLAND', 2),
(12, 'NORTH-ISLAND', 2),
(13, 'THEME-TOUR', 2),
(3, 'WEEKEND-CLUBS', NULL),
(14, 'HIKING', 3),
(15, 'PICKING', 3),
(16, 'CYCLING', 3),
(17, 'SHOOTING', 3),
(4, 'OVERSEAS', NULL),
(18, 'GROUP-TOUR', 4),
(19, 'CRUISE', 4);



INSERT INTO `Products`
(`name`, `category_id`, `price`, `description`, `stock_level`, `image_url`, `discount_details`, `status`)
VALUES
('CHENG-DU (23 May)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 99, 'CHENGDU0523.jpg', NULL, 'Available'),
('CHENG-DU (30 May)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 100, 'CHENGDU0530.jpg', NULL, 'Available'),
('CHENG-DU (6 Jun)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 100, 'CHENGDU0606.jpg', NULL, 'Available'),
('CHENG-DU (13 Jun)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 100, 'CHENGDU0613.jpg', '10%', 'Available'),
('CHENG-DU (6 Jul)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 100, 'CHENGDU0706.jpg', NULL, 'Available'),
('CHENG-DU (26 Aug)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 100, 'CHENGDU0826.jpg', NULL, 'Available'),
('CHENG-DU (5 Sep)', 5, 799, 'Discover Chengdu, the home of pandas and delicious Sichuan cuisine, on this multi-day adventure.', 100, 'CHENGDU0905.jpg', NULL, 'Available'),
('XI-AN (13 Jun)', 6, 799, 'Explore the ancient city of Xi''an, famous for its Terracotta Army, on this immersive journey.', 98, 'XIAN0613.jpg', NULL, 'Available'),
('XI-AN (10 Sep)', 6, 799, 'Explore the ancient city of Xi''an, famous for its Terracotta Army, on this immersive journey.', 100, 'XIAN0910.jpg', NULL, 'Available'),
('KUN-MING (21 Aug)', 7, 899, 'Experience the eternal spring city of Kunming with its vibrant landscapes during a multi-day tour.', 97, 'KUNMING0821.jpg', NULL, 'Available'),
('KUN-MING (22 Aug)', 7, 899, 'Experience the eternal spring city of Kunming with its vibrant landscapes during a multi-day tour.', 100, 'KUNMING0822.jpg', NULL, 'Available'),
('KUN-MING (23 Aug)', 7, 899, 'Experience the eternal spring city of Kunming with its vibrant landscapes during a multi-day tour.', 100, 'KUNMING0823.jpg', '10%', 'Available'),
('KUN-MING (28 Aug)', 7, 899, 'Experience the eternal spring city of Kunming with its vibrant landscapes during a multi-day tour.', 100, 'KUNMING0828.jpg', NULL, 'Available'),
('KUN-MING (30 Aug)', 7, 899, 'Experience the eternal spring city of Kunming with its vibrant landscapes during a multi-day tour.', 100, 'KUNMING0830.jpg', NULL, 'Available'),
('HANG-ZHOU (3 SEP)', 8, 899, 'Enjoy Hangzhou''s iconic West Lake and serene beauty in just a few days.', 96, 'HANGZHOU0903.jpg', NULL, 'Available'),
('SI-CHUAN (8 SEP)', 9, 1699, 'Immerse yourself in the stunning scenery and cultural treasures of Sichuan in this exciting adventure.', 95, 'SICHUAN0908.jpg', NULL, 'Available'),
('SAN-XIA (8 SEP)', 10, 1599, 'Cruise through the beautiful Three Gorges of the Yangtze River in a multi-day journey.', 94, 'SANXIA0908.jpg', NULL, 'Available'),
('SOUTH-ISLAND SHINING TOUR 6 DAYS (20 OCT)', 11, 2399, 'Discover the magic of New Zealand''s South Island on a 6-day adventure.', 99, 'SOUTH-ISLAND-SHINING-TOUR-6DAYS1020.jpg', '10%', 'Available'),
('SOUTH-ISLAND SHINING TOUR 6 DAYS (27 OCT)', 11, 2399, 'Discover the magic of New Zealand''s South Island on a 6-day adventure.', 100, 'SOUTH-ISLAND-SHINING-TOUR-6DAYS1027.jpg', NULL, 'Available'),
('SOUTH-ISLAND SHINING TOUR 6 DAYS (3 NOV)', 11, 2399, 'Discover the magic of New Zealand''s South Island on a 6-day adventure.', 100, 'SOUTH-ISLAND-SHINING-TOUR-6DAYS1103.jpg', NULL, 'Available'),
('SOUTH-ISLAND SHINING TOUR 6 DAYS (4 DEC)', 11, 2399, 'Discover the magic of New Zealand''s South Island on a 6-day adventure.', 100, 'SOUTH-ISLAND-SHINING-TOUR-6DAYS1204.jpg', NULL, 'Available'),
('SOUTH-ISLAND SHINING TOUR 6 DAYS (15 DEC)', 11, 2399, 'Discover the magic of New Zealand''s South Island on a 6-day adventure.', 100, 'SOUTH-ISLAND-SHINING-TOUR-6DAYS1215.jpg', NULL, 'Available'),
('SOUTH-ISLAND SHINING TOUR 6 DAYS (22 DEC)', 11, 2399, 'Discover the magic of New Zealand''s South Island on a 6-day adventure.', 100, 'SOUTH-ISLAND-SHINING-TOUR-6DAYS1222.jpg', NULL, 'Available'),
('SOUTH-ISLAND HAPPY TOUR 6 DAYS (23 OCT)', 11, 2299, 'Experience a joyful 6-day journey through the best of South Island.', 96, 'SOUTH-ISLAND-HAPPY-TOUR-6DAYS1023.jpg', NULL, 'Available'),
('SOUTH-ISLAND HAPPY TOUR 6 DAYS (30 OCT)', 11, 2299, 'Experience a joyful 6-day journey through the best of South Island.', 100, 'SOUTH-ISLAND-HAPPY-TOUR-6DAYS1030.jpg', '10%', 'Available'),
('SOUTH-ISLAND HAPPY TOUR 6 DAYS (13 NOV)', 11, 2299, 'Experience a joyful 6-day journey through the best of South Island.', 100, 'SOUTH-ISLAND-HAPPY-TOUR-6DAYS1113.jpg', NULL, 'Available'),
('SOUTH-ISLAND HAPPY TOUR 6 DAYS (20 NOV)', 11, 2299, 'Experience a joyful 6-day journey through the best of South Island.', 100, 'SOUTH-ISLAND-HAPPY-TOUR-6DAYS1120.jpg', NULL, 'Available'),
('SOUTH-ISLAND HAPPY TOUR 6 DAYS (4 DEC)', 11, 2299, 'Experience a joyful 6-day journey through the best of South Island.', 100, 'SOUTH-ISLAND-HAPPY-TOUR-6DAYS1204.jpg', NULL, 'Available'),
('SOUTH-ISLAND HAPPY TOUR 6 DAYS (11 DEC)', 11, 2299, 'Experience a joyful 6-day journey through the best of South Island.', 100, 'SOUTH-ISLAND-HAPPY-TOUR-6DAYS1211.jpg', NULL, 'Available'),
('SOUTH-ISLAND POPULAR TOUR 6 DAYS (24 OCT)', 11, 1799, 'A 6-day tour showcasing the popular highlights of South Island.', 95, 'SOUTH-ISLAND-POPULAR-TOUR-6DAYS1024.jpg', NULL, 'Available'),
('SOUTH-ISLAND POPULAR TOUR 6 DAYS (14 NOV)', 11, 1799, 'A 6-day tour showcasing the popular highlights of South Island.', 100, 'SOUTH-ISLAND-POPULAR-TOUR-6DAYS1114.jpg', '10%', 'Available'),
('SOUTH-ISLAND POPULAR TOUR 6 DAYS (5 DEC)', 11, 1799, 'A 6-day tour showcasing the popular highlights of South Island.', 100, 'SOUTH-ISLAND-POPULAR-TOUR-6DAYS1205.jpg', NULL, 'Available'),
('SOUTH-ISLAND POPULAR TOUR 6 DAYS (12 DEC)', 11, 1799, 'A 6-day tour showcasing the popular highlights of South Island.', 100, 'SOUTH-ISLAND-POPULAR-TOUR-6DAYS1212.jpg', NULL, 'Available'),
('SOUTH-ISLAND GLACIER TOUR 8 DAYS (29 OCT)', 11, 3599, 'Explore glaciers and incredible landscapes on an 8-day tour.', 100, 'SOUTH-ISLAND-GLACIER-TOUR-8DAYS1029.jpg', NULL, 'Available'),
('SOUTH-ISLAND GLACIER TOUR 8 DAYS (19 NOV)', 11, 3599, 'Explore glaciers and incredible landscapes on an 8-day tour.', 100, 'SOUTH-ISLAND-GLACIER-TOUR-8DAYS1119.jpg', '10%', 'Available'),
('SOUTH-ISLAND GLACIER TOUR 8 DAYS (29 NOV)', 11, 3599, 'Explore glaciers and incredible landscapes on an 8-day tour.', 100, 'SOUTH-ISLAND-GLACIER-TOUR-8DAYS1129.jpg', NULL, 'Available'),
('SOUTH-ISLAND GLACIER TOUR 8 DAYS (9 DEC)', 11, 3599, 'Explore glaciers and incredible landscapes on an 8-day tour.', 100, 'SOUTH-ISLAND-GLACIER-TOUR-8DAYS1209.jpg', NULL, 'Available'),
('SOUTH-ISLAND GLACIER TOUR 8 DAYS (19 DEC)', 11, 3599, 'Explore glaciers and incredible landscapes on an 8-day tour.', 100, 'SOUTH-ISLAND-GLACIER-TOUR-8DAYS1219.jpg', NULL, 'Available'),
('SOUTH-ISLAND GLACIER TOUR 8 DAYS (29 DEC)', 11, 3599, 'Explore glaciers and incredible landscapes on an 8-day tour.', 100, 'SOUTH-ISLAND-GLACIER-TOUR-8DAYS1229.jpg', '10%', 'Available'),
('SOUTH-ISLAND SCENIC TOUR 9 DAYS (26 OCT)', 11, 4299, 'Take in breathtaking views on a 9-day scenic South Island journey.', 100, 'SOUTH-ISLAND-SCENIC-TOUR-9DAYS1026.jpg', NULL, 'Available'),
('SOUTH-ISLAND SCENIC TOUR 9 DAYS (6 NOV)', 11, 4299, 'Take in breathtaking views on a 9-day scenic South Island journey.', 100, 'SOUTH-ISLAND-SCENIC-TOUR-9DAYS1106.jpg', NULL, 'Available'),
('SOUTH-ISLAND SCENIC TOUR 9 DAYS (16 NOV)', 11, 4299, 'Take in breathtaking views on a 9-day scenic South Island journey.', 100, 'SOUTH-ISLAND-SCENIC-TOUR-9DAYS1116.jpg', NULL, 'Available'),
('SOUTH-ISLAND SCENIC TOUR 9 DAYS (26 NOV)', 11, 4299, 'Take in breathtaking views on a 9-day scenic South Island journey.', 100, 'SOUTH-ISLAND-SCENIC-TOUR-9DAYS1126.jpg', '10%', 'Available'),
('SOUTH-ISLAND SCENIC TOUR 9 DAYS (6 DEC)', 11, 4299, 'Take in breathtaking views on a 9-day scenic South Island journey.', 100, 'SOUTH-ISLAND-SCENIC-TOUR-9DAYS1206.jpg', NULL, 'Available'),
('NORTH-ISLAND MAGIC TOUR 2 DAYS (8 OCT)', 12, 899, 'A 2-day magical adventure through New Zealand''s North Island.', 98, 'NORTH-ISLAND-MAGIC-TOUR-2DAYS1008.jpg', NULL, 'Available'),
('NORTH-ISLAND MAGIC TOUR 2 DAYS (19 NOV)', 12, 899, 'A 2-day magical adventure through New Zealand''s North Island.', 100, 'NORTH-ISLAND-MAGIC-TOUR-2DAYS1119.jpg', NULL, 'Available'),
('NORTH-ISLAND CLASSIC TOUR 3 DAYS (25 NOV)', 12, 1299, 'Enjoy classic North Island highlights over 3 days.', 94, 'NORTH-ISLAND-CLASSIC-TOUR-3DAYS1125.jpg', NULL, 'Available'),
('NORTH-ISLAND CLASSIC TOUR 3 DAYS (28 DEC)', 12, 1299, 'Enjoy classic North Island highlights over 3 days.', 100, 'NORTH-ISLAND-CLASSIC-TOUR-3DAYS1228.jpg', '10%', 'Available'),
('NORTH-ISLAND BAY OF ISLANDS TOUR 3 DAYS (21 NOV)', 12, 1199, 'Explore the beautiful Bay of Islands in this 3-day North Island tour.', 100, 'NORTH-ISLAND-BOI-TOUR-3DAYS1121.jpg', NULL, 'Available'),
('NORTH-ISLAND PANORAMIC 5 DAYS (21 DEC)', 12, 1999, 'Take in sweeping views on this 5-day panoramic tour of the North Island.', 100, 'NORTH-ISLAND-PANORAMIC-TOUR-5DAYS1221.jpg', NULL, 'Available'),
('THEME TOUR GOLF 7 DAYS (20 NOV)', 13, 3999, 'Enjoy a 7-day golf-themed holiday in stunning settings.', 97, 'THEME-TOUR-GOLF-7DAYS1120.jpg', NULL, 'Available'),
('THEME TOUR THRILLING 7 DAYS (2 SEP)', 13, 4299, 'An action-packed 7-day adventure for thrill-seekers.', 100, 'THEME-TOUR-THRILLING-7DAYS0902.jpg', NULL, 'Available'),
('THEME TOUR THRILLING 7 DAYS (2 DEC)', 13, 4299, 'An action-packed 7-day adventure for thrill-seekers.', 100, 'THEME-TOUR-THRILLING-7DAYS1202.jpg', NULL, 'Available'),
('THEME TOUR THRILLING 7 DAYS (15 DEC)', 13, 4299, 'An action-packed 7-day adventure for thrill-seekers.', 100, 'THEME-TOUR-THRILLING-7DAYS1215.jpg', NULL, 'Available'),
('THEME TOUR SKI 3 DAYS (12 AUG)', 13, 610, 'Choose between 3-day ski adventures, perfect for winter enthusiasts.', 93, 'THEME-TOUR-SKI-3DAYS0812.jpg', '10%', 'Available'),
('THEME TOUR SKI 3 DAYS (12 SEP)', 13, 610, 'Choose between 3-day ski adventures, perfect for winter enthusiasts.', 100, 'THEME-TOUR-SKI-3DAYS0912.jpg', NULL, 'Available'),
('THEME TOUR SKI 3 DAYS (12 SEP)', 13, 610, 'Choose between 3-day ski adventures, perfect for winter enthusiasts.', 100, 'THEME-TOUR-SKI-3DAYS0912.jpg', NULL, 'Available'),
('THEME TOUR SKI 4 DAYS (22 JUL)', 13, 990, 'Choose between 4-day ski adventures, perfect for winter enthusiasts.', 100, 'THEME-TOUR-SKI-4DAYS0722.jpg', NULL, 'Available'),
('THEME TOUR SKI 4 DAYS (2 OCT)', 13, 990, 'Choose between 4-day ski adventures, perfect for winter enthusiasts.', 100, 'THEME-TOUR-SKI-4DAYS1002.jpg', NULL, 'Available'),
('THEME TOUR SKI 5 DAYS (15 SEP)', 13, 1325, 'Choose between 5-day ski adventures, perfect for winter enthusiasts.', 100, 'THEME-TOUR-SKI-5DAYS0915.jpg', '10%', 'Available'),
('THEME TOUR SKI 5 DAYS (29 SEP)', 13, 1325, 'Choose between 5-day ski adventures, perfect for winter enthusiasts.', 100, 'THEME-TOUR-SKI-5DAYS0929.jpg', NULL, 'Available'),
('THEME TOUR RV TAURANGA 3 DAYS (28 OCT)', 13, 610, 'Experience the freedom of a 3-day RV adventure to Tauranga.', 100, 'THEME-TOUR-RV-TAURANGA-3DAYS1028.jpg', NULL, 'Available'),
('THEME TOUR RV TAURANGA 3 DAYS (13 NOV)', 13, 610, 'Experience the freedom of a 3-day RV adventure to Tauranga.', 100, 'THEME-TOUR-RV-TAURANGA-3DAYS1113.jpg', NULL, 'Available'),
('THEME TOUR RV COROMANDEL 3 DAYS (28 NOV)', 13, 610, 'Experience the freedom of a 3-day RV adventure to Coromandel.', 100, 'THEME-TOUR-RV-COROMANDEL-3DAYS1128.jpg', NULL, 'Available'),
('HIKING GOLDMINE 1 DAY (7 SEP)', 14, 129, 'A 1-day hike through the historic Goldmine Trail.', 99, 'HIKING-GOLDMINE-1DAY0907.jpg', NULL, 'Available'),
('HIKING GOLDMINE 1 DAY (9 NOV)', 14, 129, 'A 1-day hike through the historic Goldmine Trail.', 100, 'HIKING-GOLDMINE-1DAY1109.jpg', NULL, 'Available'),
('HIKING GOLDMINE 1 DAY (30 NOV)', 14, 129, 'A 1-day hike through the historic Goldmine Trail.', 100, 'HIKING-GOLDMINE-1DAY1130.jpg', NULL, 'Available'),
('HIKING MAUAO 1 DAY (14 SEP)', 14, 129, 'Trek the scenic trails of Mauao over one day.', 100, 'HIKING-MAUAO-1DAY0914.jpg', NULL, 'Available'),
('HIKING MAUAO 1 DAY (19 OCT)', 14, 129, 'Trek the scenic trails of Mauao over one day.', 100, 'HIKING-MAUAO-1DAY1019.jpg', NULL, 'Available'),
('HIKING MAUAO 1 DAY (16 NOV)', 14, 129, 'Trek the scenic trails of Mauao over one day.', 100, 'HIKING-MAUAO-1DAY1116.jpg', NULL, 'Available'),
('HIKING CLIFFWALK 1 DAY (21 SEP)', 14, 129, 'Enjoy stunning views on this 1-day cliff walk adventure.', 100, 'HIKING-CLIFFWALK-1DAY0921.jpg', NULL, 'Available'),
('HIKING CLIFFWALK 1 DAY (26 OCT)', 14, 129, 'Enjoy stunning views on this 1-day cliff walk adventure.', 100, 'HIKING-CLIFFWALK-1DAY1026.jpg', '10%', 'Available'),
('HIKING CLIFFWALK 1 DAY (23 NOV)', 14, 129, 'Enjoy stunning views on this 1-day cliff walk adventure.', 100, 'HIKING-CLIFFWALK-1DAY1123.jpg', NULL, 'Available'),
('PICKING STRAWBERRY 1 DAY (2 NOV)', 15, 129, 'Spend a fun day picking strawberries.', 98, 'PICKING-STRAWBERRY-1DAY1102.jpg', NULL, 'Available'),
('PICKING STRAWBERRY 1 DAY (3 NOV)', 15, 129, 'Spend a fun day picking strawberries.', 100, 'PICKING-STRAWBERRY-1DAY1103.jpg', NULL, 'Available'),
('PICKING STRAWBERRY 1 DAY (14 DEC)', 15, 129, 'Spend a fun day picking strawberries.', 100, 'PICKING-STRAWBERRY-1DAY1214.jpg', NULL, 'Available'),
('PICKING STRAWBERRY 1 DAY (15 DEC)', 15, 129, 'Spend a fun day picking strawberries.', 100, 'PICKING-STRAWBERRY-1DAY1215.jpg', '10%', 'Available'),
('PICKING BLUEBERRY 1 DAY (21 DEC)', 15, 129, 'Enjoy a day picking fresh blueberries.', 100, 'PICKING-BLUEBERRY-1DAY1221.jpg', NULL, 'Available'),
('PICKING BLUEBERRY 1 DAY (22 DEC)', 15, 129, 'Enjoy a day picking fresh blueberries.', 100, 'PICKING-BLUEBERRY-1DAY1222.jpg', NULL, 'Available'),
('PICKING FLOWER 1 DAY (9 NOV)', 15, 129, 'Experience flower picking in beautiful gardens.', 100, 'PICKING-FLOWER-1DAY1109.jpg', NULL, 'Available'),
('PICKING FLOWER 1 DAY (23 NOV)', 15, 129, 'Experience flower picking in beautiful gardens.', 100, 'PICKING-FLOWER-1DAY1123.jpg', NULL, 'Available'),
('CYCLING HAURAKI 1 DAY (30 NOV)', 16, 299, 'A 1-day cycling adventure along the Hauraki Rail Trail.', 97, 'CYCLING-HAURAKI-1DAY1130.jpg', NULL, 'Available'),
('CYCLING HAURAKI 1 DAY (7 DEC)', 16, 299, 'A 1-day cycling adventure along the Hauraki Rail Trail.', 100, 'CYCLING-HAURAKI-1DAY1207.jpg', NULL, 'Available'),
('CYCLING WAIHEKE 1 DAY (12 OCT)', 16, 299, 'Explore the beauty of Waiheke Island by bike for one day.', 100, 'CYCLING-WAIHEKE-1DAY1012.jpg', '10%', 'Available'),
('CYCLING WAIHEKE 1 DAY (27 OCT)', 16, 299, 'Explore the beauty of Waiheke Island by bike for one day.', 100, 'CYCLING-WAIHEKE-1DAY1027.jpg', NULL, 'Available'),
('SHOOTING 1 DAY (24 NOV)', 17, 349, 'A thrilling 1-day shooting experience.', 96, 'SHOOTING-1DAY1124.jpg', NULL, 'Available'),
('SHOOTING 1 DAY (1 DEC)', 17, 349, 'A thrilling 1-day shooting experience.', 100, 'SHOOTING-1DAY1201.jpg', NULL, 'Available'),
('SHOOTING 1 DAY (1 DEC)', 17, 349, 'A thrilling 1-day shooting experience.', 100, 'SHOOTING-1DAY1201.jpg', NULL, 'Available'),
('SILK ROAD TOUR 15 DAYS (1 SEP)', 18, 3999, 'Embark on a 15-day journey along the ancient Silk Road with an Auckland-based tour leader and all-inclusive service.', 99, 'SILK-ROAD-TOUR-15DAYS0901.jpg', NULL, 'Available'),
('EUROPE TOUR 30 DAYS (19 SEP)', 18, 16999, 'Experience the best of Europe in 30 days, including an Auckland tour leader and an all-inclusive package.', 100, 'EUROPE-TOUR-30DAYS0919.jpg', NULL, 'Available'),
('THAILAND TOUR 8 DAYS (4 SEP)', 18, 1599, 'Explore the wonders of Thailand on an 8-day all-inclusive tour with a dedicated tour leader from Auckland.', 100, 'THAILAND-TOUR-8DAYS0904.jpg', NULL, 'Available'),
('SOUTH AMERICA TOUR 21 DAYS (3 NOV)', 18, 15999, 'Discover South America on a 21-day adventure, guided by an Auckland tour leader, with everything included.', 98, 'SOUTH-AMERICA-TOUR-21DAYS1103.jpg', NULL, 'Available'),
('SPAIN & PORTUGAL TOUR 14 DAYS (11 OCT)', 18, 15999, 'Enjoy the culture and cuisine of Spain and Portugal in 14 days, with an Auckland-based guide and all-inclusive service.', 100, 'SPAIN&PORTUGAL-TOUR-14DAYS1011.jpg', NULL, 'Available'),
('YUNNAN TOUR 12 DAYS (22 OCT)', 18, 1799, 'Experience the stunning landscapes of Yunnan on a 12-day all-inclusive journey led by a tour leader from Auckland.', 100, 'YUNNAN-TOUR-12DAYS1022.jpg', NULL, 'Available'),
('ERBIN TOUR 8 DAYS (27 DEC)', 18, 2299, 'Explore Erbin’s vibrant culture over 8 days, with an Auckland-based tour leader and all-inclusive package.', 97, 'ERBIN-TOUR-8DAYS1227.jpg', NULL, 'Available'),
('AUSTRALIA SEACATION CRUISE TOUR 4 DAYS (3 OCT 2026)', 19, 1110, 'Enjoy a relaxing 4-day cruise vacation in Australia.', 96, 'AUSTRALIASEACATION-CRUISETOUR-4DAYS261003.jpg', '10%', 'Available'),
('AUSTRALIA SEACATION CRUISE TOUR 5 DAYS (4 NOV 2025)', 19, 1223, 'Enjoy a relaxing 4-day cruise vacation in Australia.', 100, 'AUSTRALIASEACATION-CRUISETOUR-5DAYS250411.jpg', NULL, 'Available'),
('AUSTRALIA & NEW ZEALAND SEACATION CRUISE TOUR 13 DAYS (28 FEB 2025)', 19, 4429, 'Discover Australia and New Zealand on a 13-day cruise.', 95, 'AUSTRALIANEWZEALAND-CRUISETOUR-13DAYS250228.jpg', '10%', 'Available'),
('TAHITI HAWAII SOUTH PACIFIC CRUISE TOUR 17 DAYS (4 OCT 2024)', 19, 3876, 'A luxurious 17-day cruise through Tahiti, Hawaii, and the South Pacific.', 94, 'TAHITIHAWAIISOUTHPACIFIC-CRUISETOUR-17DAYS241004.jpg', NULL, 'Available');

#
# INSERT INTO `Accounts` (`account_id`, `customer_id`, `credit_limit`, `outstanding_balance`, `invoice_due_date`, `invoice_frequency`)
# VALUES
# (1, 1, 1000.00, 500.00, '2024-06-15', 'Monthly'),
# (2, 3, 1000.00, 1000.00, '2024-06-15', 'Monthly'),
# (3, 4, 1000.00, 950.00, '2024-06-15', 'Monthly'),
# (4, 5, 1000.00, 400.00, '2024-06-15', 'Monthly'),
# (5, 6, 1000.00, 100.00, '2024-06-15', 'Monthly'),
# (6, 7, 1000.00, 300.00, '2024-06-15', 'Monthly'),
# (7, 8, 1000.00, 530.00, '2024-06-15', 'Monthly'),
# (8, 9, 1000.00, 20.00, '2024-06-15', 'Monthly');


# INSERT INTO Messages (sender_id, recipient_id, message_type, message_content, message_date, reply_status)
# VALUES
#
# (1, 16, 'standard', 'Meeting scheduled for next week.', '2024-05-25 14:00:00', 'waiting for reply'),
# (2, 17, 'standard', 'Reminder: Team lunch on Friday.', '2024-05-25 14:15:00', 'waiting for reply'),
# (3, 18, 'standard', 'Quarterly report submission deadline.', '2024-05-25 14:30:00', 'waiting for reply'),
# (4, 19, 'standard', 'Feedback on the recent presentation.', '2024-05-25 14:45:00', 'waiting for reply'),
# (5, 20, 'standard', 'Please confirm your attendance for the workshop.', '2024-05-25 15:00:00', 'waiting for reply'),
# (6, 16, 'standard', 'Team meeting notes and action items.', '2024-05-25 15:15:00', 'waiting for reply'),
# (7, 17, 'standard', 'Invitation to company event.', '2024-05-25 15:30:00', 'waiting for reply'),
# (8, 18, 'standard', 'Monthly performance review schedule.', '2024-05-25 15:45:00', 'waiting for reply'),
# (26, 1, 'standard', 'Applying for credit for new equipment.', '2024-06-01 10:00:00', 'waiting for reply'),
# (17, 1, 'standard', 'Inquiry about order status.', '2024-06-01 11:30:00', 'replied'),
# (17, 2, 'standard', 'Requesting credit limit increase.', '2024-06-01 14:45:00', 'waiting for reply'),
# (26, 9,	'reply_credit',	'approve, 1000', '2024-06-03 14:44:35','waiting for reply');

