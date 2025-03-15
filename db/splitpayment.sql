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
INSERT INTO SplitPayments (SplitPaymentID,OrderID,PayerUserID, Amount, TransactionID, Status)
VALUES 
(1, 1, 1, 50.00, 2004, 'Successful'),
(2, 2, 2, 50.00, 2005, 'Successful'),
(3, 3, 3, 50.00, 2006, 'Successful'),
(4, 4, 4, 40.00, 2007, 'Pending'),
(5, 5, 5, 35.00, 2008, 'Pending'),
(6, 6, 6, 40.00, 2009, 'Successful'),
(7, 7, 7, 40.00, 2010, 'Successful'),
(8, 8, 8, 40.00, 2011, 'Successful') ;



