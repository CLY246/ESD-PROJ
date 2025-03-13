-- Create the database
DROP DATABASE IF EXISTS ErrorLog;
CREATE DATABASE ErrorLog;

-- Select the database
USE ErrorLog;

-- ErrorLog Table
CREATE TABLE ErrorLog (
    ErrorID INT PRIMARY KEY AUTO_INCREMENT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ServiceName VARCHAR(100),  -- e.g., "PaymentService", "QueueManagement"
    OrderID INT NULL,          -- Could be NULL if not related to an order
    ErrorDetails TEXT,
    Severity VARCHAR(20)      -- e.g., "Info", "Warning", "Error", "Critical"
);

-- ErrorLog Table Data
INSERT INTO ErrorLog (ServiceName, OrderID, ErrorDetails, Severity)
VALUES 
('PaymentService', 4, 'Payment failed due to insufficient funds in the account.', 'Critical'),
('PaymentService', 9, 'Payment failed due to a timeout while processing the transaction.', 'Error');
