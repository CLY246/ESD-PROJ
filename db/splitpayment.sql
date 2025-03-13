-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS SplitPayment;
USE SplitPayment;

-- Create SplitPayments Table
CREATE TABLE SplitPayments (
    SplitPaymentID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL,          -- Order associated with the split payment
    PayerUserID INT NOT NULL,      -- User making the payment
    Amount DECIMAL(10,2) NOT NULL, -- Amount for the split payment
    TransactionID INT NULL,        -- Associated transaction (if any)
    Status VARCHAR(50) DEFAULT 'Pending' -- Payment status (Pending, Completed, Failed)
);

-- Insert Additional Sample Data
INSERT INTO SplitPayments (OrderID, PayerUserID, Amount, TransactionID, Status)
VALUES 
(1004, 5, 60.00, 2004, 'Completed'),
(1004, 6, 40.00, NULL, 'Pending'),
(1005, 7, 55.00, 2005, 'Completed'),
(1006, 8, 85.00, NULL, 'Failed'),
(1007, 9, 95.50, 2006, 'Pending'),
(1007, 10, 104.50, NULL, 'Pending'),
(1008, 11, 30.00, 2007, 'Completed'),
(1009, 12, 70.00, 2008, 'Completed'),
(1010, 13, 110.00, NULL, 'Failed'),
(1011, 14, 150.00, 2009, 'Completed');
