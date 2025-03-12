-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS quickreorder;
USE quickreorder;

-- Create QuickReorders Table
CREATE TABLE QuickReorders (
    QuickReorderID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,         -- User who created the quick reorder
    OrderID INT NOT NULL,        -- Associated order ID
    ReorderName VARCHAR(255) NULL -- Optional custom name for the reorder
);

-- Insert Additional Sample Data
INSERT INTO QuickReorders (UserID, OrderID, ReorderName)
VALUES 
(5, 1005, 'Home Improvement'),
(6, 1006, 'Pet Supplies'),
(7, 1007, 'Holiday Gifts'),
(8, 1008, 'Back to School'),
(9, 1009, 'Electronics Reorder'),
(10, 1010, 'Fitness Equipment'),
(11, 1011, 'Kitchen Appliances'),
(12, 1012, NULL),
(13, 1013, 'Car Maintenance'),
(14, 1014, 'Work Essentials');
