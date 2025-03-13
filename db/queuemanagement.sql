-- Create the database
DROP DATABASE IF EXISTS QueueManagement;
CREATE DATABASE QueueManagement;

-- Select the database
USE QueueManagement;

-- OrderQueue Table
CREATE TABLE OrderQueue (
    QueueID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL UNIQUE, 
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    EstimatedWaitTime INT,
    Status VARCHAR(50) -- "Queued", "Processing", "Completed"
);

-- OrderQueue Table Data
INSERT INTO OrderQueue (OrderID, EstimatedWaitTime, Status) VALUES
(101, 10, 'Queued'),
(102, 5, 'Processing'),
(103, 8, 'Queued'),
(104, 12, 'Queued'),
(105, 7, 'Processing'),
(106, 15, 'Queued'),
(107, 3, 'Processing'),
(108, 20, 'Queued'),
(109, 6, 'Completed'),
(110, 14, 'Queued');