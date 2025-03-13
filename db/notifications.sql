-- Create the database
DROP DATABASE IF EXISTS Notifications;
CREATE DATABASE Notifications;

-- Select the database
USE Notifications;


-- Notification Table
CREATE TABLE Notifications (
    NotificationID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    OrderID INT NOT NULL, -- Make it NOT NULL if always tied to an order
    NotificationType ENUM('Order Update', 'Payment Confirmation', 'Delivery Update', 'Promotion') NOT NULL, -- ENUM for fixed values
    Message TEXT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsRead BOOLEAN DEFAULT FALSE
);

-- Notifications Table Data
INSERT INTO Notifications (UserID, OrderID, NotificationType, Message, IsRead) VALUES
(1, 101, 'Order Update', 'Your order has been placed successfully.', FALSE),
(2, 102, 'Payment Confirmation', 'Your payment for Order 102 has been received.', TRUE),
(3, 103, 'Delivery Update', 'Your order is out for delivery.', FALSE),
(4, 104, 'Order Update', 'Your order has been placed successfully.', FALSE),
(5, 105, 'Payment Confirmation', 'Your payment for Order 105 has been received.', TRUE),
(6, 106, 'Delivery Update', 'Your order is arriving soon.', FALSE),
(7, 107, 'Order Update', 'Your order has been placed successfully.', FALSE),
(8, 108, 'Payment Confirmation', 'Your payment for Order 108 has been received.', TRUE),
(9, 109, 'Delivery Update', 'Your order has been delivered.', TRUE),
(10, 110, 'Order Update', 'Your order has been placed successfully.', FALSE);
