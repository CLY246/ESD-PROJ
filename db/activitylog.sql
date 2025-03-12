-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS activitylog;
USE activitylog;

-- Create ActivityLog Table
CREATE TABLE ActivityLog (
    ActivityID INT PRIMARY KEY AUTO_INCREMENT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UserID INT NULL,        -- Foreign key to User service (if applicable)
    OrderID INT NULL,       -- Foreign key to Order service (if applicable)
    EventType VARCHAR(100) NOT NULL, -- e.g., "Order Placed", "Payment Received", "Notification Sent"
    Details TEXT NULL
);

-- Insert Dummy Data into ActivityLog
INSERT INTO ActivityLog (UserID, OrderID, EventType, Details)
VALUES 
(1, 101, 'Order Placed', 'User 1 placed an order with OrderID 101.'),
(2, 102, 'Payment Received', 'Payment confirmed for OrderID 102.'),
(3, 103, 'Notification Sent', 'User 3 was notified about their order delivery.'),
(4, 104, 'Order Placed', 'User 4 placed an order with OrderID 104.'),
(5, 105, 'Payment Received', 'Payment confirmed for OrderID 105.'),
(6, 106, 'Notification Sent', 'User 6 was notified about their order delivery.'),
(7, 107, 'Order Placed', 'User 7 placed an order with OrderID 107.'),
(8, 108, 'Payment Received', 'Payment confirmed for OrderID 108.'),
(9, 109, 'Notification Sent', 'User 9 was notified about their order delivery.'),
(10, 110, 'Order Placed', 'User 10 placed an order with OrderID 110.');