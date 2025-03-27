-- Create the database
DROP DATABASE IF EXISTS ErrorLog;
CREATE DATABASE ErrorLog;

-- Select the database
USE ErrorLog;

-- ErrorLog Table
CREATE TABLE ErrorLog (
    ErrorID INT PRIMARY KEY AUTO_INCREMENT,
    Error_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Error_Details VARCHAR(1000) NOT NULL
);

-- ErrorLog Table Data
INSERT INTO ErrorLog (Error_Details)
VALUES 
('Payment failed due to insufficient funds in the account.'),
('Payment failed due to a timeout while processing the transaction.');
